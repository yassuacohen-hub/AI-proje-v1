# -*- coding: utf-8 -*-
"""web_sitesi_zenginlestir regresyon mandallari (D-66).

Olcum 2026-10-04 (`scripts/web_kaynak_olcum.py`, canli DB):
    website_domain bos 7343 · dolu 2780 · bos alanli ham adayi 2614 ·
    **sablonsuz bos alanli ham adayi 0**. Bu dosyanin varlik nedeni:
    `raw_website` uzerinden doldurma yolu olcumle REDDEDILDI; tek yol
    arama -> canli dogrulama.

Ag YOK: `arama` ve `ceki` parametreleri enjekte edilir. Test kirliligini
kendisi uretmez (D-243) — dolayisiyla bu dosya `pytest` ile asla ag acmaz.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from company_master.etl import web_sitesi_zenginlestir as mod
from company_master.etl.web_sitesi_zenginlestir import (
    aday_domainler,
    icerik_dogrula,
    unvan_anahtar_kelimeler,
    zenginlestir,
)

#: Marka kelimeleri **sektor kelimesi DEGILDIR** (D-245, olcum: 10123 unvan).
#: Once fixture "ARITES METAL" idi; `metal` unvanlarin %5'inde gectigi icin
#: `GENEL_KELIMELER`'e girdi ve 5 test kirmizi verdi. Bu dogru bir red: sektor
#: kelimesi marka kaniti degildir. Fixture gercek bir marka yaziyor.
UNVAN = "ARİTES NORD SANAYİ VE TİCARET LTD. ŞTİ."
GECERLI_ICERIK = ("ARİTES NORD SAN. VE TİC. LTD. ŞTİ. — nord örgü işleme, "
                  "CNC tezgah, oto yedek parça. Ankara OSTİM. " * 6)


# ---------------------------------------------------------------- saf katman

def test_turkce_katlama_once_yapilir():
    """'İ'.lower() birlesik nokta uretir: once katla, sonra kucult.

    Regresyon: once kucultuldugunde 'TİCARET' -> 'ti̇caret' bolunup
    sahte 'caret' kelimesi uretiyordu; boylece 'nord' gecen unvanda
    'nord' + 'caret' cikiyor, 'ticaret' cikmiyordu.
    """
    k = unvan_anahtar_kelimeler(UNVAN)
    assert "arites" in k, k
    assert "nord" in k, k
    assert "caret" not in k, k
    assert "ticaret" not in k, k


def test_sektor_kelimesi_marka_sayilmaz():
    """D-245: doluluk gecerlilik degil. `METAL` unvanlarin %5.2'sinde gecigi
    icin ayirt edici DEGIL; `akinasmetal.com.tr` gibi her makine sitesinde
    gecer. Pilot 3 bunu kanitladi: `AKIN MAKINA...` -> `ostimbul.com`
    yalnizca sektor kelimeleriyle "gecti"."""
    assert "metal" not in unvan_anahtar_kelimeler("ARİTES METAL SAN. LTD.")
    assert "makina" not in unvan_anahtar_kelimeler("AKIN MAKİNA SAN. LTD.")
    assert "ostim" not in unvan_anahtar_kelimeler("X OSTİM HİZMET SAN. LTD.")
    k = unvan_anahtar_kelimeler("ARİTES NORD SAN. LTD.")
    assert k == ("arites", "nord"), k


def test_sirfce_kelimeler_duser():
    k = unvan_anahtar_kelimeler(UNVAN)
    assert not ({"sanayi", "ticaret", "ltd", "sti", "san", "tic"} & set(k)), k


def test_kisa_kelime_almaz():
    # 4 karakterden kisa kelime ayirt edici degildir ("ABC PLASTIK").
    assert "abc" not in unvan_anahtar_kelimeler("ABC PLASTİK SAN. LTD.")
    assert "nord" in unvan_anahtar_kelimeler("ABC NORD SAN. LTD.")
    # Sektor kelimesi de duser: unvan tamamen ayirt edicisiz kalir -> bos tuple.
    assert unvan_anahtar_kelimeler("ABC PLASTİK SAN. LTD.") == ()


def test_yas_kelime_yoksa_liste_bos():
    assert unvan_anahtar_kelimeler("SAN. VE TİC. LTD. ŞTİ.") == ()
    assert unvan_anahtar_kelimeler("") == ()
    assert unvan_anahtar_kelimeler(None) == ()


# ------------------------------------------------------------ aday eleme

def _sonuc(*url_list):
    return {"results": [{"url": u} for u in url_list]}


def test_aday_sirasi_korunur_ve_tekilleştirilir():
    a = aday_domainler(UNVAN, _sonuc(
        "https://aritesmetal.com.tr/",
        "http://www.aritesmetal.com.tr/iletisim",
        "https://ikinci-site.com.tr",
    ))
    assert [h for h, _ in a] == ["aritesmetal.com.tr", "ikinci-site.com.tr"], a
    assert a[0][1] == "https://aritesmetal.com.tr/"


def test_sosyal_medya_ve_pazar_yeri_elenir():
    a = aday_domainler(UNVAN, _sonuc(
        "https://facebook.com/aritesmetal",
        "https://www.linkedin.com/company/arites",
        "https://www.sahibinden.com/firma",
        "https://tr.wikipedia.org/wiki/Arites"))
    assert a == [], a


def test_sablon_ve_kaynak_domain_elenir():
    """Olcum: bos alanli 2614 firmanin ham adayi %100 bu listede."""
    a = aday_domainler(UNVAN, _sonuc(
        "https://www.isim.org.tr/firma/arites",
        "https://ostim.org.tr/uye/arites",
        "https://www.ostimistihdam.com/ilan/arites",
        "https://aso.org.tr/uye/arites"))
    assert a == [], a


def test_kamu_domaini_elenir():
    a = aday_domainler(UNVAN, _sonuc("https://www.ticaret.gov.tr/firma",
                                    "https://ankara.bel.tr/x",
                                    "https://universite.edu.tr/f"))
    assert a == [], a


def test_gecersiz_bicim_elenir():
    a = aday_domainler(UNVAN, _sonuc("https://localhost:8080/x", "not-a-url",
                                    "https://arites metal.com.tr"))
    assert a == [], a


def test_yas_anahtarli_unvan_tum_adaylari_eler():
    """Sirfce kelimesi olan unvanda ADAY BILDIRILMEZ (3.7 saglama sart)."""
    assert aday_domainler("SAN. VE TİC. LTD. ŞTİ.", _sonuc(
        "https://aritesmetal.com.tr")) == []


def test_arama_sonucu_bilinmeyen_bicim():
    """Bilinmeyen bicim 'sonuc yok' sayilir — sessizce aday uretilmez."""
    assert aday_domainler(UNVAN, {"weird": "bicim"}) == []
    assert aday_domainler(UNVAN, None) == []
    assert aday_domainler(UNVAN, _sonuc()) == []


# ------------------------------------------------------- icerik dogrulama

def test_gecerli_sayfa_kabul():
    g, s = icerik_dogrula(GECERLI_ICERIK, UNVAN, alan_adi="https://aritesnord.com.tr")
    assert g, s
    assert "marka domain'de" in s, s


def test_alan_adi_verilmezse_kabul_EDILMEZ():
    """Sahiplik yalniz domain ile kanitlanir. Alan adi verilmeden
    icerik eslesmesi **kanit degildir** — eskiden burasi kabul ediyordu."""
    g, s = icerik_dogrula(GECERLI_ICERIK, UNVAN)
    assert not g
    assert s.startswith("sahiplik_kaniti_yok"), s


def test_baska_firma_sayfasi_reddedilir():
    """Ayni sektordeki baska firmanin sayfasi 200 donse de reddedilir."""
    g, s = icerik_dogrula("KOMSUDUZ MAKINA SANAYI A.S. — CNC tezgah. " * 12,
                          UNVAN, alan_adi="https://aritesnord.com.tr")
    assert not g, s


def test_kisa_icerik_reddedilir():
    g, s = icerik_dogrula("ARITES NORD", UNVAN, alan_adi="https://aritesnord.com.tr")
    assert not g and s.startswith("icerik_kisa"), s


def test_bos_icerik_reddedilir():
    assert icerik_dogrula("", UNVAN, alan_adi="https://aritesnord.com.tr") == \
        (False, "icerik_bos")


def test_parklanmis_alan_adi_reddedilir():
    g, s = icerik_dogrula("This domain is for sale. ARITES NORD. " * 12, UNVAN,
                          alan_adi="https://aritesnord.com.tr")
    assert not g and s.startswith("parklanmis"), s


def test_anahtar_kelimesi_gecmeyen_reddedilir():
    g, s = icerik_dogrula("Biz bir yazilim sirketiyiz. Urunlerimiz var. " * 12,
                          UNVAN)
    assert not g and s.startswith("unvan_kelimesi_gecmiyor"), s


# ------------------------------------------- pilot 2026-10-04: 5 canli firma

#: Pilot 3/5 "dogrulandi" dedi; elde incelendi, **1'i gercek FP**'ydi:
#: `BERAT MAK.` -> `info-albania.com` = Arnavutluk/Berat sehirinin turizm
#: rehberi. Eslesen kelime "berat" idi: 5 karakter, domain'de **yok**,
#: ikinci kelime yok. Bu ucu mandalla kilitli.
BERAT_TURIZM_SAYFASI = (
    "Berat Guide - Explore the beautiful city of Berat in Albania. "
    "Discover Berat Castle, the Mangalem quarter and Berat's history. "
    "Plan your trip to Berat with our travel guide and itineraries. " * 4)


def test_zayif_tek_eslesme_reddedilir():
    """5 karakterlik tek kelime, domain'de yok -> kabul edilmez."""
    g, s = icerik_dogrula(BERAT_TURIZM_SAYFASI, "BERAT MAK.",
                          alan_adi="https://www.info-albania.com")
    assert not g, s
    assert s.startswith("sahiplik_kaniti_yok"), s


def test_tek_kelimeye_indigen_unvan_ELLE_GEREKLI():
    """Pilot 3 (2026-10-04): `BERAT MAK.` -> `beratmakinam.com` sayfasi gercekten
    "BERAT MAKINA" diyor, ama:
      * unvan tek ayirt edici kelimeye ("berat") iniyor,
      * sayfa SEO kelime yigini ("ahsap isleme, ahsap isleme makinalari, ..." tekrar),
      * DB'deki unvan kisaltilmis; ayni adi tasiyan baska firmalar olabilir.
    Tek kelime + marka domain = KANIT DEGIL -> otomatik yazilmaz, adaya duser."""
    g, s = icerik_dogrula("Berat Makinacilik — ahsap isleme makinalari. " * 8,
                          "BERAT MAK.", alan_adi="https://beratmakinam.com")
    assert not g, s
    assert "tek_anahtar_kelime_elle_gerekli" in s, s


def test_tek_kelime_diger_hostta_daha_da_zayif():
    g, s = icerik_dogrula("Berat Makinacilik uretimi. " * 8,
                          "BERAT MAK.", alan_adi="https://ornek-firma.net")
    assert not g, s
    assert s.startswith("sahiplik_kaniti_yok"), s


def test_iki_kelime_gecse_AMA_MARKA_DOMAINDE_YOKSA_YETMEZ():
    """Pilot 4 (2026-10-04) canli FP: `ÖZLEM ÇİÇEKCILIK` ->
    `cicekrehberi.net`. Icetikte hem "ozlem" hem "cicek" geciyor; eski kural
    ("domain'de ya da 2 kelime") bunu **kabul** ediyordu ve dizin sayfasi
    yazilacakti. Sahiplik yalniz domain ile kanitlanir."""
    g, s = icerik_dogrula(
        "Ozlem Cicekcilik - canli cicek gonderme. Rehberde Ozlem Cicek. " * 8,
        "ÖZLEM ÇİÇEKÇILIK", alan_adi="https://cicekrehberi.net")
    assert not g, s
    assert s.startswith("sahiplik_kaniti_yok"), s


def test_ozlem_gercek_sahibi_gecer():
    """Ayni unvan, marka domain'de -> gecer. Yanlis pozitifi silmek,
    dogru eslesmeyi de silmemek demektir."""
    g, s = icerik_dogrula(
        "Ozlem Cicekcilik - Ankara. Canli cicek gonderme. " * 8,
        "ÖZLEM ÇİÇEKÇILIK", alan_adi="https://ozlemcicekcilik.com")
    assert g, s


def test_iki_kelime_gecse_kabul_OLMADI():
    """Cift kelime + marka domain'de dogru eslesmedir."""
    g, s = icerik_dogrula("Gezen Ic Dis Ticaret ve Cadir Sanayi Ltd. " * 8,
                          "GEZEN GRUP İÇ DIŞ TİC. VE ÇADIR SAN. LTD. ŞTİ.",
                          alan_adi="https://gezencadir.com")
    assert g, s
    assert "marka domain'de" in s, s


def test_alti_karakterli_tek_kelime_YETMEZ():
    """Pilot 2. tur FP: `MERCAN MAK.` -> `8438-tr.all.biz` "mercan" (6) ile
    gecti. Iki kapi birden kapandi: dizin listesi + sahiplik kaniti."""
    g, s = icerik_dogrula("Mercan Is Makinalari satis ve servis. " * 8,
                          "MERCAN MAK.", alan_adi="https://8438-tr.all.biz")
    assert not g, s
    assert s.startswith("sahiplik_kaniti_yok"), s


def test_uzun_kelime_diger_firma_sayfasinda_YETMEZ():
    """Pilot 2. tur FP: `ÖZLEM ÇIÇEKCILIK` -> `alocicek.com`; "cicekcilik"
    10 karakterdi ve baska bir cicekcinin sayfasinda gecti."""
    g, s = icerik_dogrula("Alo Cicek - canli cicek gonderme. " * 10,
                          "ÖZLEM ÇİÇEKÇILIK", alan_adi="https://alocicek.com")
    assert not g, s


def test_mkb_hidrolik_sahiplik_yok():
    """Pilot 3 FP: `MKB HİDROLİK SİSTEMLER...` -> `mkbhidrolik.com`.
    `mkb` 3 karakter; marka domain'de **yok**. Once kabul ediyordu."""
    g, s = icerik_dogrula("MKB Hidrolik Sistemler - hidrolik baglanti. " * 8,
                          "MKB HİDROLİK SİSTEMLER VE MÜH. MAK. SAN. TİC.",
                          alan_adi="https://mkb.com.tr")
    assert not g, s
    assert s.startswith("sahiplik_kaniti_yok"), s


def test_gomap_pilot4_yurt_cakismasi_FP():
    """Pilot 4 canli FP: `GOMAP MÜH. MÜŞAVİRLİK... LTD. ŞTİ.` -> `gomap.be`.
    Marka domain'de VARDI ve icerik gecti; sayfa `GOMAP SCS`
    (BCE0806.750.087) yani **Belcika** sirketi. Sahiplik kaniti bunu
    yakalamaz — domain gercekten o markaya ait. Ayirici: Turk sirket turu
    + yurt disi alan adi -> `el_tasidi`."""
    satir = mod._satir_isle(
        {"company_id": 7},
        "GOMAP MÜH. MÜŞAVİRLİK DAN. VE ARAŞT. TİC. LTD. ŞTİ.",
        arama=lambda u: _sonuc("https://gomap.be"),
        ceki=lambda url: ("Gomap est une société de services dédiés aux "
                          "évènements publics. GOMAP SCS BCE0806.750.087. " * 8, ""))
    assert satir["kabul"] is False and satir["domain"] is None, satir
    assert satir["el_tasidi"] and "yurt_kakismasi" in satir["el_tasidi"][0]["sebep"], satir


def test_yurt_kakismasi_kurali():
    U = "GOMAP MÜH. MÜŞAVİRLİK DAN. VE ARAŞT. TİC. LTD. ŞTİ."
    assert mod.yurt_kakismasi_olasilik(U, "https://gomap.be")
    assert mod.yurt_kakismasi_olasilik(U, "https://gomap.com")
    assert not mod.yurt_kakismasi_olasilik(U, "https://gomap.com.tr")
    # Turk sirket turu yoksa (sahis adli/cerdan) kapı devre disi
    assert not mod.yurt_kakismasi_olasilik("MEHMET SOYALP", "https://soyalp.be")


def test_b2b_dizin_domaini_aday_bile_sayilmaz():
    """Dizin listesi adayı eler; icerik dogrulamaya hic gelmez."""
    a = aday_domainler("MERCAN MAK.", _sonuc(
        "https://8438-tr.all.biz/company",
        "https://www.kompass.com/company/mercan",
        "https://mercanmakina.com.tr"))
    assert [h for h, _ in a] == ["mercanmakina.com.tr"], a


def test_kendi_adini_tasiyan_domain_elenmez():
    """Alt dize eslesmesi hatasi: liste `firma.com` iceriyor,
    `a-firma.com.tr` kendi adini tasiyan bir firma — elenmemeli."""
    assert not mod._dagitici_mi("https://a-firma.com.tr")
    assert mod._dagitici_mi("https://firma.com")
    assert mod._dagitici_mi("https://www.kompass.com/tr")
    a = aday_domainler("A FİRMA MAK.", _sonuc("https://a-firma.com.tr"))
    assert [h for h, _ in a] == ["a-firma.com.tr"], a


def test_adres_alani_html_etiketi_yazmaz():
    """Pilot: `Adres:` satirinda `</div><div class="textwidget"><p>` geldi."""
    ham = ('</div><div class="textwidget"><p>Yakacik Mh. 3907. Sok. No:6 '
           'Yenimahalle / ANKARA</p>')
    aday = mod._adres_adayi(f"Adres: {ham}")
    assert aday and "<" not in aday and ">" not in aday, aday
    assert aday.startswith("Yakacik Mh."), aday


def test_kisa_adres_parcasi_aday_degil():
    assert mod._adres_adayi("Adres: <p>4. cad.</p>") is None
    assert mod._adres_adayi("Ankara") is None


# ------------------------------------------------- satir zinciri (5 adim)

@pytest.fixture
def izin_acik(monkeypatch):
    """Izin kapisini ac; kapi testinin konusu degil, zincirin konusu."""
    from company_master.etl.scrape_kayit import KazimaYazici
    monkeypatch.setattr(KazimaYazici, "izin_var",
                        staticmethod(lambda url: (True, "test")))


def test_basari_zinciri(izin_acik):
    satir = mod._satir_isle(
        {"company_id": 1}, UNVAN,
        arama=lambda u: _sonuc("https://aritesmetal.com.tr"),
        ceki=lambda url: (GECERLI_ICERIK, ""))
    assert satir["domain"] == "https://aritesmetal.com.tr", satir
    assert satir["kabul"] is True
    assert satir["sebep"].startswith("eslesti"), satir


def test_izin_reddi_aday_yazmaz(izin_acik, monkeypatch):
    """Izin kapisi kapaliysa domain YAZILMAZ; sebep izlenebilir olur."""
    from company_master.etl.scrape_kayit import KazimaYazici
    monkeypatch.setattr(KazimaYazici, "izin_var",
                        staticmethod(lambda url: (False, "robots.txt: /")))
    satir = mod._satir_isle(
        {"company_id": 1}, UNVAN,
        arama=lambda u: _sonuc("https://aritesmetal.com.tr"),
        ceki=lambda url: (GECERLI_ICERIK, ""))
    assert satir["domain"] is None and satir["kabul"] is False
    assert "izin_yok" in satir["sebep"], satir
    # Her adayin gerekcesi ayri ayri gorunur (tek `sebep` son adayi gostermisti)
    assert satir["aday_denemeleri"] == [
        {"domain": "https://aritesmetal.com.tr",
         "sebep": "izin_yok: robots.txt: /"}], satir


def test_izin_aciksa_iceriğe_bakilir(izin_acik, monkeypatch):
    """Izin acik + 200 + yanlis icerik = yine yazmaz (saglam zincir)."""
    satir = mod._satir_isle(
        {"company_id": 1}, UNVAN,
        arama=lambda u: _sonuc("https://aritesmetal.com.tr"),
        ceki=lambda url: ("KOMSUDUZ MAKINA SANAYI A.S. " * 14, ""))
    assert satir["domain"] is None and satir["kabul"] is False


def test_http_hatasi_kayda_girilir(izin_acik):
    satir = mod._satir_isle(
        {"company_id": 1}, UNVAN,
        arama=lambda u: _sonuc("https://aritesmetal.com.tr"),
        ceki=lambda url: ("", "HTTP 503"))
    assert satir["domain"] is None and "503" in satir["sebep"], satir


def test_arama_hatasi_yutulmaz():
    def patlatir(unvan):
        raise RuntimeError("9Router yok")

    satir = mod._satir_isle({"company_id": 1}, UNVAN, arama=patlatir,
                            ceki=lambda url: ("", ""))
    assert satir["domain"] is None
    assert satir["sebep"].startswith("arama_hatasi"), satir


def test_adaylarin_hepsi_dogrulanmazsa_yazmaz(izin_acik):
    satir = mod._satir_isle(
        {"company_id": 1}, UNVAN,
        arama=lambda u: _sonuc("https://a-firma.com.tr", "https://b-firma.com.tr"),
        ceki=lambda url: ("", "HTTP 404"))
    assert satir["domain"] is None and satir["kabul"] is False
    assert "404" in satir["sebep"], satir


# ---------------------------------------------------------- yazma kapisi

class _SayanEngine:
    """Yazma cagrilarini SAYAN sahte baglanti; hicbir sey gercekten yazmaz.

    `connect()` ve `begin()` ayni sahte baglantiyi dondurur (SQLAlchemy
    Connection gibi davranir), boylece modulun ayrimi olmadan test edilebilir.
    """

    def __init__(self):
        self.kayitli = []

    def execute(self, statement, params=None):
        self.kayitli.append((str(getattr(statement, "text", statement)), params))
        return self

    def first(self):
        return None

    def scalar(self):
        return 1

    @property
    def rowcount(self):
        return 1

    def connect(self):
        return self

    def begin(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _sql_metni(baglanti_kaydi, onek, tam=False):
    """Kayitli ilk SQL metni; `tam=True` ise metin+parametre dondurur."""
    sql, params = next((s, p) for s, p in baglanti_kaydi
                       if s.lstrip().startswith(onek))
    return (sql, params) if tam else sql


def test_kuru_yazmaz(izin_acik):
    """Varsayilan `kuru=True` hicbir SQL yazmaz (D-243: yesil test gormez)."""
    engine = _SayanEngine()
    ozet = zenginlestir(engine, kuru=True,
                        hedefler=[{"company_id": 1, "legal_name": UNVAN}],
                        arama=lambda u: _sonuc("https://aritesmetal.com.tr"),
                        ceki=lambda url: (GECERLI_ICERIK, ""))
    assert ozet["dogrulanan"] == 1, ozet
    assert ozet["yazilan"] == 0
    assert engine.kayitli == [], engine.kayitli


def test_yazma_yalniz_bos_alana(izin_acik):
    """UPDATE her alan icin `IS NULL` korumasi tasiyan tek SQL'dir."""
    engine = _SayanEngine()
    kayit = {"company_id": 1, "domain": "https://aritesmetal.com.tr",
             "telefon": "+903121234567", "eposta": "info@aritesmetal.com.tr",
             "adres": None, "sebep": "eslesti", "kaynak_url": "x"}
    mod._yaz(engine, 7, 1, UNVAN, kayit)
    guncellemeler = [s for s, _ in engine.kayitli if s.lstrip().startswith("UPDATE")]
    assert len(guncellemeler) == 3, guncellemeler  # address None -> atlanir
    sql = " ".join(guncellemeler)
    assert sql.count("IS NULL") == 3 and "btrim" in sql, sql
    for alan in ("website_domain", "primary_phone", "primary_email"):
        assert alan in sql, alan
    assert "address" not in sql, "adres adayi yoksa UPDATE uretilmemeli"
    assert engine.kayitli[0][1]["cid"] == 1


def test_kaynak_izi_idempotent(izin_acik):
    """`source_records` yazimi ON CONFLICT ile tekrar calistirilabilir."""
    engine = _SayanEngine()
    kayit = {"company_id": 42, "domain": "https://aritesmetal.com.tr",
             "telefon": None, "eposta": None, "adres": None, "sebep": "eslesti"}
    mod._yaz(engine, 7, 42, UNVAN, kayit)
    sql, params = _sql_metni(engine.kayitli, "INSERT INTO source_records",
                             tam=True)
    assert "ON CONFLICT (source_id, external_id)" in sql, sql
    assert params["eid"] == "web:42", params


def test_nace_ipucu_yalniz_raw_payloadda(izin_acik):
    """NACE/Ağırlık dokunulmaz (0,3/10): ipucu puana girmez."""
    engine = _SayanEngine()
    kayit = {"company_id": 1, "domain": "https://aritesmetal.com.tr",
             "telefon": None, "eposta": None, "adres": None, "sebep": "eslesti"}
    mod._yaz(engine, 7, 1, UNVAN, kayit)
    sql, params = next((s, p) for s, p in engine.kayitli
                       if s.lstrip().startswith("INSERT INTO source_records"))
    assert "nace_tahmin" in params["payload"]
    assert "nace_code" not in sql and "nace_score" not in sql


def test_kaynak_kaydi_idempotent_ve_tipli():
    engine = _SayanEngine()
    mod._kaynak_id(engine)
    sql, params = next((s, p) for s, p in engine.kayitli
                       if s.lstrip().startswith("INSERT INTO sources"))
    assert params["ad"] == mod.KAYNAK_ADI
    assert "'company_website'" in sql, sql
    assert "ON CONFLICT DO NOTHING" in sql, sql
