# -*- coding: utf-8 -*-
"""ASO ingest glob ve yazma biçimi mandalları.

Kök neden (ölçüldü): eski `ingest_aso.py` `*.csv`+`*.json` globuyordu;
`data/aso/aso_full_clean_report.json` firma kaydı sanılıp
`read_json(lines=True)` ile okunuyor ve `Expected object or value` patlıyordu.
Ayrıca JSONL alanı `Firma Adı` değil `unvan` — eşleşme olmayınca
`legal_name` üretilmiyordu.
"""

import ast
import inspect
import json
from pathlib import Path

import pytest

from company_master.etl import ingest_aso

ROOT = Path(__file__).resolve().parents[1]


def _yaz(dizin, ad, icerik):
    yol = dizin / ad
    if ad.endswith(".jsonl"):
        yol.write_text("\n".join(json.dumps(k, ensure_ascii=False) for k in icerik), encoding="utf-8")
    else:
        yol.write_text(icerik, encoding="utf-8")
    return yol


class TestKaynakDosya:
    def test_rapor_dosyasi_secilmez(self, tmp_path):
        """Rapor/özet dosyası varken ham JSONL seçilir."""
        _yaz(tmp_path, "aso_full_clean_report.json", '{"rapor": true}')
        _yaz(tmp_path, "aso_full.jsonl", [{"unvan": "A A.Ş."}])
        assert ingest_aso.kaynak_dosya(tmp_path).name == "aso_full.jsonl"

    def test_csv_json_globu_kullanilmaz(self, tmp_path):
        """Klasörde csv/json varken bile JSONL yoksa dosya bulunmaz."""
        _yaz(tmp_path, "rapor.json", "{}")
        _yaz(tmp_path, "liste.csv", "a,b")
        assert ingest_aso.kaynak_dosya(tmp_path) is None

    def test_eksik_dosya_none_doner(self, tmp_path):
        assert ingest_aso.kaynak_dosya(tmp_path) is None


class TestSatirlariHazirla:
    def test_unvan_legal_name_olur(self):
        """Alan adı `unvan`; eski eşleşme `Firma Adı` idi ve tutmuyordu."""
        satirlar = ingest_aso.satirlari_hazirla([{"unvan": "ABC METAL SAN. A.Ş."}])
        assert satirlar[0]["legal_name"] == "ABC METAL SAN. A.Ş."

    def test_bos_unvan_atlanir(self):
        assert ingest_aso.satirlari_hazirla([{"unvan": ""}, {"unvan": None}, {}]) == []

    def test_batch_ici_mukerrer_tekillestirilir(self):
        satirlar = ingest_aso.satirlari_hazirla(
            [{"unvan": "ABC A.Ş."}, {"unvan": "ABC A.Ş."}, {"unvan": "abc a.ş."}]
        )
        assert len(satirlar) == 1

    def test_tasfiye_oneki_ayri_firma_yazilmaz(self):
        """D-264: önek bir hâldir, soyulmaz."""
        satirlar = ingest_aso.satirlari_hazirla(
            [{"unvan": "(İFLAS NEDENİYLE) TASFİYE HALİNDE ABC A.Ş."}]
        )
        assert satirlar[0]["legal_name"].startswith("(İFLAS NEDENİYLE)")

    def test_telefon_sozluk_ve_duz_metin(self):
        assert ingest_aso.satirlari_hazirla(
            [{"unvan": "A", "telefonlar": [{"no": "03121234567"}]}]
        )[0]["primary_phone"] == "03121234567"
        assert ingest_aso.satirlari_hazirla(
            [{"unvan": "B", "telefonlar": ["03129876543"]}]
        )[0]["primary_phone"] == "03129876543"


class TestYazmaBicimi:
    def test_insert_on_conflict_dogru_kullaniyor(self):
        """D-244: toplu append UNIQUE index'te batch'i patlatir."""
        sql = str(ingest_aso.INSERT_SQL)
        assert "ON CONFLICT" in sql and "legal_name" in sql

    def test_append_ve_tosql_kullanilmaz(self):
        kaynak = inspect.getsource(ingest_aso)
        assert "to_sql" not in kaynak
        assert "if_exists='append'" not in kaynak

    def test_vergi_numarasi_kolonu_yazilmaz(self):
        """D-246: ASO'nun sicil numarası VKN değildir."""
        kaynak = inspect.getsource(ingest_aso)
        assert "tax_number" not in ingest_aso.INSERT_SQL._bindparams
        assert "tax_number" in kaynak  # yalnız yorumda geçer

    def test_olu_kolon_yazilmaz(self):
        """D-259: data_quality_score pasifleştirildi."""
        assert "data_quality_score" not in str(ingest_aso.INSERT_SQL)


class TestBozukSatir:
    def test_bozuk_satir_atlanir(self, tmp_path):
        yol = tmp_path / "aso_full.jsonl"
        yol.write_text(
            '{"unvan": "A A.Ş."}\nbozuk\n{"unvan": "B A.Ş."}\n', encoding="utf-8"
        )
        assert len(ingest_aso.kayitlari_oku(yol)) == 2


class TestImportKoku:
    """Modül iki farklı yoldan çağrılıyor; ikisi de çalışmalı.

    `refresh_pipeline.py:85` bu modülü `src.company_master.etl.ingest_aso`
    olarak içe aktarır ve `sys.path`'te yalnız ROOT vardır (`src/` yok).
    Mutlak `company_master.*` importları burada `ModuleNotFoundError`
    veriyordu. Kardeş modül `normalize.py` göreli import kullanır; aynı
    desen burada da zorunludur.
    """

    def test_mutlak_company_master_importu_yok(self):
        kaynak = inspect.getsource(ingest_aso)
        assert "\nfrom company_master" not in kaynak
        assert "\nimport company_master" not in kaynak

    def test_goreli_import_kullanilir(self):
        kaynak = inspect.getsource(ingest_aso)
        assert "from ..db.connection import get_engine" in kaynak
        assert "from .kimlik_no import" in kaynak
        # Ice aktarilan ad gercekten kullanilir (D-211: ikiz yol yok).
        assert "sicil_dogrula" in kaynak

    def test_src_on_ekli_yoldan_ice_aktarilabilir(self):
        """refresh_pipeline.py'nin kullandığı yoldan import çözmeli."""
        import importlib
        import sys
        from pathlib import Path

        kok = str(Path(ingest_aso.__file__).resolve().parents[3])
        if kok not in sys.path:
            sys.path.insert(0, kok)
        try:
            modul = importlib.import_module("src.company_master.etl.ingest_aso")
            assert modul.KAYNAK_DOSYA == "aso_full.jsonl"
        finally:
            sys.modules.pop("src.company_master.etl.ingest_aso", None)


# --- D-211: ikiz ingest yolu kapatildi -------------------------------------

ESKI_SCRIPT = ROOT / "scripts" / "ingest_aso_data.py"


class TestIkizYolYok:
    """Ölçüm: eski scriptin canlı Python çağıranı yoktu. Kanonik yol
    `src/company_master/etl/ingest_aso.py`.

    D-224 notu: brifte "12 doküman referansı" yazıyordu; yeniden ölçüldü
    ve **yanlıştı**. Gerçekte 4 yer: 2 tarihsel hub satırı (D-223 gereği
    geriye dönük değiştirilmez), brifin kendisi, bu test. Aktif çağıran yok.
    """

    def test_eski_script_diskte_yok(self):
        assert not ESKI_SCRIPT.exists(), (
            "D-211: ikiz ingest yolu " + str(ESKI_SCRIPT) + " hala duruyur."
        )

    def test_tek_yazma_yolu(self):
        """`ekle()` yerine `yaz()`; eski yardimci bir ikiz olurdu."""
        assert hasattr(ingest_aso, "yaz")
        assert not hasattr(ingest_aso, "ekle")

    def test_extract_vkn_ozelligi_tasinmadi(self):
        """D-246: unvandan 10-11 haneli sayı çıkarmak VKN uydurmaktır."""
        kaynak = inspect.getsource(ingest_aso)
        assert "VKN_PATTERN" not in kaynak
        assert "extract_vkn" not in kaynak

    def test_clean_unvan_ile_tasfiye_oneki_soyulmez(self):
        """D-264: eski script oneki soyuyordu; önek bir hâldir."""
        assert not hasattr(ingest_aso, "clean_unvan")
        satirlar = ingest_aso.satirlari_hazirla(
            [{"unvan": "(İFLAS NEDENİYLE) TASFİYE HALİNDE ABC A.Ş."}]
        )
        assert satirlar[0]["legal_name"].startswith("(İFLAS NEDENİYLE)")


# --- D-233: eslesme YALNIZ kesindir ---------------------------------------

LIKE_DESENI = ("LIKE", "ILIKE", "~*", "SIMILAR TO")


def _modul_agaci(modul):
    return ast.parse(inspect.getsource(modul))


def _cagrilan_adlar(modul):
    """Cagrilan fonksiyon adlari. Docstring/yorum DEGIL, gercek cagri olcer.

    D-245 (doldurulmusluk gecerlilik degildir) mandala da uygulanir:
    kurali ANLATAN metin, kurali CAGIRMAMAKTIR.
    """
    adlar = set()
    for dugum in ast.walk(_modul_agaci(modul)):
        if isinstance(dugum, ast.Call):
            hedef = dugum.func
            if isinstance(hedef, ast.Name):
                adlar.add(hedef.id)
            elif isinstance(hedef, ast.Attribute):
                adlar.add(hedef.attr)
    return adlar


def _kod_metinleri(modul):
    """Yalnizca SQL/ifade sabitleri. Docstring ve yorum sayilmaz.

    Neden AST: metin taramasi kural metnini de yakalar. Modulun
    docstring'i fuzzy yasagini ANLATIYOR; onu ihlal sayan bir mandal
    kurali degil, gürültü üretir (D-266: mandal kendi kör noktasını korur).
    """
    docstringler = set()
    for dugum in ast.walk(_modul_agaci(modul)):
        if isinstance(dugum, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            metin = ast.get_docstring(dugum, clean=False)
            if metin:
                docstringler.add(metin)
    return [
        dugum.value
        for dugum in ast.walk(_modul_agaci(modul))
        if isinstance(dugum, ast.Constant)
        and isinstance(dugum.value, str)
        and dugum.value not in docstringler
    ]


class TestKesinEslesme:
    def test_like_temelli_eslesme_yok(self):
        for metin in _kod_metinleri(ingest_aso):
            for desen in LIKE_DESENI:
                assert desen not in metin, (
                    "D-233: fuzzy eslesme (" + desen + ") ikiz scriptten tasinmadi."
                )

    def test_mandal_kirilabilir(self):
        """D-256/4: mandal kırılarak doğrulanır.

        Bu kayıp, fuzzy eşleşmenin yeniden yazılmadığını değil, **yazıldığı
        hâlde yakalanmadığını** kanıtlar.
        """
        sahte = ast.parse("SORGULAR = [\"SELECT 1 WHERE legal_name LIKE :p\"]")
        ifade = [
            d.value
            for d in ast.walk(sahte)
            if isinstance(d, ast.Constant) and isinstance(d.value, str)
        ]
        assert any("LIKE" in m for m in ifade), "mandal kirilan kodda da yakalamali"

    def test_cagri_mandali_kirilabilir(self):
        """D-245/256: cagri tabanli mandal da kırılarak doğrulanır."""
        sahte = ast.parse("def f():\n    return kimlik_dogrula('1')\n")
        adlar = {
            d.func.id
            for d in ast.walk(sahte)
            if isinstance(d, ast.Call) and isinstance(d.func, ast.Name)
        }
        assert "kimlik_dogrula" in adlar

    def test_eslesme_normalize_esittir(self):
        sql = str(ingest_aso.ESLES_SQL)
        assert "LOWER(TRIM(legal_name)) = LOWER(TRIM(:unvan))" in sql

    def test_eslesme_tekil_satir_dondurur(self):
        assert "LIMIT 1" in str(ingest_aso.ESLES_SQL)


# --- D-244 / D-263: kaynak izi ve idempotency -----------------------------

class TestKaynakKaydi:
    def test_source_records_yazimi_var(self):
        assert "INSERT INTO source_records" in str(ingest_aso.KAYNAK_SQL)

    def test_idempotency_kisiti_kullanilir(self):
        """Aynı (source_id, external_id) ikinci koşuda yeni satır açmaz."""
        sql = str(ingest_aso.KAYNAK_SQL)
        assert "ON CONFLICT (source_id, external_id)" in sql

    def test_ham_kayit_guncellenir_ama_bos_alan_ezilmez(self):
        sql = str(ingest_aso.KAYNAK_SQL)
        assert "COALESCE(source_records.raw_address, EXCLUDED.raw_address)" in sql
        assert "COALESCE(source_records.raw_phone, EXCLUDED.raw_phone)" in sql
        assert "COALESCE(source_records.raw_email, EXCLUDED.raw_email)" in sql

    def test_sicil_numarasi_ham_kimlik_kolona_yazilmaz(self):
        """D-246: `ticaretSicilNo` VKN değildir; raw_payload'ta durur."""
        assert "raw_tax_number" not in ingest_aso.KAYNAK_SQL._bindparams
        assert "NULL, :raw_nace" in str(ingest_aso.KAYNAK_SQL)

    def test_sicil_raw_payload_icerisinde_korunur(self):
        satirlar = ingest_aso.satirlari_hazirla(
            [{"unvan": "A A.Ş.", "ticaretSicilNo": "123456"}]
        )
        assert satirlar[0]["raw_payload"]["ticaretSicilNo"] == "123456"
        assert satirlar[0]["raw_payload"]["kaynak"] == "aso.org.tr"

    def test_null_raw_payload_birlestirmesi_guvenli(self):
        """D-245: doluluk degil gecerlilik; NULL birlestirme sessizce yutar.

        `NULL || '{...}'` Postgres'te NULL verir; yani mevcut kaydin ham
        verisi bu guncellemede **kaybolur** ve hicbir hata vermez.
        """
        sql = str(ingest_aso.KAYNAK_SQL)
        assert "COALESCE(source_records.raw_payload" in sql
        assert "COALESCE(EXCLUDED.raw_payload" in sql
        assert "source_records.raw_payload || EXCLUDED.raw_payload" not in sql

    def test_bagli_company_id_yazilir(self):
        """D-263: kayıt hangi firmaya ait olmalı."""
        assert "company_id" in ingest_aso.KAYNAK_SQL._bindparams

    def test_dolu_a_yonu_ezilmez(self):
        """D-263: `companies.source_record_id` kaynaktır, COALESCE korur."""
        assert "COALESCE(source_record_id, :sid)" in str(ingest_aso.BAGLA_SQL)


class TestExternalId:
    """D-262: UNIQUE kısıt NULL'a bağlanmaz; kimlik üretilmezse atlanır."""

    def test_sicil_once_gelir(self):
        satirlar = ingest_aso.satirlari_hazirla(
            [{"unvan": "A", "ticaretSicilNo": "111", "detailToken": "222"}]
        )
        assert satirlar[0]["external_id"] == "111"

    def test_sicil_yoksa_detail_token_yedegi(self):
        satirlar = ingest_aso.satirlari_hazirla([{"unvan": "A", "detailToken": "222"}])
        assert satirlar[0]["external_id"] == "222"

    def test_ikisi_de_yoksa_kimliksiz(self):
        assert ingest_aso.satirlari_hazirla([{"unvan": "A"}])[0]["external_id"] is None


class TestContentHash:
    """D-261: hash yalnız içerikten; her koşuda yeni satır açmaz."""

    def test_anahtar_sirasi_degistirmez(self):
        a = ingest_aso._content_hash({"unvan": "A", "adres": "X"})
        b = ingest_aso._content_hash({"adres": "X", "unvan": "A"})
        assert a == b

    def test_icerik_degistirilince_hash_degisir(self):
        a = ingest_aso._content_hash({"unvan": "A"})
        b = ingest_aso._content_hash({"unvan": "B"})
        assert a != b

    def test_zaman_damgasi_hash_girdisi_degil(self):
        """Satır kimliği/collected_at karışırsa her koşu yeni satır açar."""
        kaynak = inspect.getsource(ingest_aso)
        assert "collected_at" not in kaynak
        assert "NOW()" not in kaynak.split("def _content_hash")[1].split("def ")[0]


# --- D-245: doluluk eslesme, zenginlestirme yalniz bos alana ---------------

class TestZenginlestirme:
    def test_dolu_alan_ezilmez(self):
        sql = str(ingest_aso.ZENGINLESTIR_SQL)
        for kolon in ("address", "primary_phone", "primary_email"):
            assert "COALESCE(NULLIF(%s, '')" % kolon in sql

    def test_vergi_no_kolonu_hic_yazilmaz(self):
        """Eski script `vergi_no` ve `description` kolonlarini yaziyordu."""
        kaynak = inspect.getsource(ingest_aso)
        assert "vergi_no" not in kaynak
        assert "description" not in kaynak

    def test_verilmedigi_alan_yazilmaz(self):
        assert ingest_aso._zenginlestirilebilir(
            {"address": None, "primary_phone": None, "primary_email": None}
        ) is False
        assert ingest_aso._zenginlestirilebilir({"primary_phone": "0312"}) is True


class TestYazilmayanKolonlar:
    """D-246/D-259: bu üç kolon bu yoldan yazılmaz."""

    @pytest.mark.parametrize("kolon", ["tax_number", "raw_tax_number", "data_quality_score"])
    def test_sql_ifadelerinde_gecmiyor(self, kolon):
        for ifade in (
            ingest_aso.INSERT_SQL,
            ingest_aso.ESLES_SQL,
            ingest_aso.ZENGINLESTIR_SQL,
            ingest_aso.BAGLA_SQL,
        ):
            assert kolon not in ifade._bindparams
            assert kolon not in str(ifade)

    @pytest.mark.parametrize("kolon", ["tax_number", "raw_tax_number", "data_quality_score"])
    def test_sozlesmede_beyan_ediyor(self, kolon):
        assert kolon in ingest_aso.YAZILMAZ_KOLONLAR


class TestSicilKapisi:
    """D-267: ticaret sicili kendi kapısından geçer, VKN kapısından değil.

    Ölçüldü: eski ölçüm `kimlik_dogrula()` kullanıyordu ve 1091/1091
    "geçersiz" diyordu. Bu alarm değil, kapının yanlış seçildiğinin
    işaretiydi — 3-6 haneli sicil zaten VKN değildir.
    """

    def test_vkn_kapisi_kullanilmaz(self):
        assert "kimlik_dogrula" not in _cagrilan_adlar(ingest_aso)
        assert "sicil_dogrula" in _cagrilan_adlar(ingest_aso)

    def test_sicil_kapisi_kullanilir(self):
        assert ingest_aso.gecersiz_sicil_sayisi([]) == 0
        gecerli = [{"unvan": "A", "ticaretSicilNo": "123456"}]
        assert ingest_aso.gecersiz_sicil_sayisi(gecerli) == 0

    def test_bos_sicil_sayilmaz(self):
        assert ingest_aso.gecersiz_sicil_sayisi(
            [{"unvan": "A", "ticaretSicilNo": None}, {"unvan": "B"}]
        ) == 0


# --- D-233: turetilmis dosya ikiz degil, bagimliliktir --------------------

TEMIZ_DOSYA = ROOT / "data" / "aso" / "aso_full_clean.jsonl"
CANLI_TUKETICI = ROOT / "scripts" / "osb_tarama.py"


class TestTuretilmisDosyaIstisnasi:
    """Brif "turetilmis dosyalari tasi" diyordu; olcum yanlisladi.

    `aso_full_clean.jsonl` 716 tekil unvan / 781 `?` isaretli tutuyor ve
    `scripts/osb_tarama.py` KORUNAN listesinde. Canli kod bu yola bakiyorsa
    yol kopya degil **bagimliliktir** (D-233). Silinmez; yalniz OSB tuketicisi
    once kanonik dosyaya gecirilirse anlamli olur.
    """

    def test_dosya_yerinde_duruyor(self):
        assert TEMIZ_DOSYA.exists(), (
            "D-233: OSB tuketicisi kanonik dosyaya gecirilmeden bu dosya silinmez."
        )

    def test_kanonik_yol_clean_dosya_degil(self):
        assert ingest_aso.KAYNAK_DOSYA == "aso_full.jsonl"
        assert "clean" not in ingest_aso.KAYNAK_DOSYA

    def test_canli_bagimlilik_korunuyor(self):
        """Dosya silinirse bu test kirar: once tuketiciyi gecirmek gerekir."""
        kaynak = CANLI_TUKETICI.read_text(encoding="utf-8")
        assert "aso_full_clean.jsonl" in kaynak


# --- D-243: prova diske yazmaz ---------------------------------------------

class TestDryRun:
    def test_engine_olmadan_calisir(self):
        """Prova engine'e hiç dokunmaz; DB'ye yazmaz."""
        satirlar = ingest_aso.satirlari_hazirla([{"unvan": "A A.Ş."}])
        olcum = ingest_aso.yaz(None, satirlar, dry_run=True)
        assert olcum["eklenen"] == 0
        assert olcum["kaynak_yazilan"] == 0

    def test_kimliksiz_sayi_beklenmedik_yazilir(self):
        satirlar = ingest_aso.satirlari_hazirla([{"unvan": "A A.Ş."}])
        assert ingest_aso.yaz(None, satirlar, dry_run=True)["kaynak_atlanan"] == 1

    def test_bos_liste_erken_doner(self):
        assert ingest_aso.yaz(None, [], dry_run=False)["eklenen"] == 0
