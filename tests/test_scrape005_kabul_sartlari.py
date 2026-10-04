# -*- coding: utf-8 -*-
"""SCRAPE-005 kabul şartları — orkestratör kararı 2026-10-03.

Karar: [[SCRAPE-005-KAZIMA-DOCKER-INTEGRATION_karar_2026-10-03]]
Rapor: [[SCRAPE-005-KAZIMA-DOCKER-INTEGRATION_rapor_2026-10-02_uretim]]

Kapsam: 5 kabul şartının kodla doğrulanabilen olanları.
Canlı koşu kanıtı (kabul 3) rapor dosyasında; burada ölçülemez.
"""
import ast
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "docker-compose.yml"
REFRESH = ROOT / "scripts" / "refresh_pipeline.py"
PIPELINE = ROOT / "src" / "company_master" / "etl" / "pipeline.py"


def _kazima_service() -> dict:
    """docker-compose.yml içinden kazima servisini çözümler."""
    import yaml

    veri = yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))
    return veri["services"]["kazima"]


def _fonksiyon_kaynagi(dosya: pathlib.Path, ad: str) -> str:
    agac = ast.parse(dosya.read_text(encoding="utf-8"))
    for dugum in ast.walk(agac):
        if isinstance(dugum, (ast.FunctionDef, ast.AsyncFunctionDef)) and dugum.name == ad:
            return ast.get_source_segment(dosya.read_text(encoding="utf-8"), dugum) or ""
    raise AssertionError(f"{dosya.name} içinde {ad}() bulunamadı")


# --- Karar 1: compose DATABASE_URL satiri kalksin, env_file tek kaynak ---


class TestKarar1ComposeDatabaseUrl:
    def test_kazima_environmentde_database_url_yok(self):
        """İki kaynak = iki gerçek. environment'ta DATABASE_URL olmamalı."""
        env = _kazima_service().get("environment") or {}
        anahtarlar = (
            list(env.keys())
            if isinstance(env, dict)
            else [satir.split("=", 1)[0] for satir in env]
        )
        assert "DATABASE_URL" not in anahtarlar, (
            f"environment içinde DATABASE_URL var: {anahtarlar}. "
            "env_file tek kaynak olmalı (karar 1)."
        )

    def test_kazima_env_file_kullanir(self):
        assert _kazima_service().get("env_file"), "env_file yok; canlı DB'ye bağlanamaz"

    def test_yerel_db_adresi_kazimada_yok(self):
        ham = COMPOSE.read_text(encoding="utf-8")
        blok = ham[ham.index("kazima:"):]
        blok = blok[: blok.index("\n  ")] if "\n  " in blok else blok
        assert "db:5432" not in blok, "kazima hala yerel db:5432 adresine bagli"

    def test_ayri_kazima_database_url_degiskeni_yok(self):
        """Karar 1: KAZIMA_DATABASE_URL diye ikinci bir kaynak YAPILMAZ."""
        ham = COMPOSE.read_text(encoding="utf-8")
        assert "KAZIMA_DATABASE_URL" not in ham


# --- Karar 2: refresh_pipeline.py:67 gercek import yolu ---


class TestKarar2ImportYolu:
    def test_detay_scraper_import_yolu_dogru(self):
        kaynak = REFRESH.read_text(encoding="utf-8")
        assert (
            "from src.company_master.etl.scrapers.ostim_detail_scraper import run_scraper"
            in kaynak
        ), "import yolu gercek dosya yolunu kullanmiyor (karar 2)"

    def test_eski_yanlis_yol_kalmamis(self):
        kaynak = REFRESH.read_text(encoding="utf-8")
        assert "from src.company_master.etl.ostim_detail_scraper" not in kaynak

    def test_import_edilen_dosya_diskte_var(self):
        """Import yazıyor ama hedef yoksa adım sessizce başarısız olur."""
        hedef = ROOT / "src" / "company_master" / "etl" / "scrapers" / "ostim_detail_scraper.py"
        assert hedef.exists(), f"hedef dosya yok: {hedef}"

    def test_import_yolu_ureti_ile_cozuluyor(self):
        """Import satırı gerçekten Python'un çözebildiği bir yola mı işaret ediyor?

        NOT: `step_detail_scrape()` burada ÇALIŞTIRILMAZ — OSTİM'ye ağ isteği
        atar ve kabul şartı kanıtı üretmez. Bunun yerine yalnız modül çözümü
        denetlenir (import hatası canlı ağa çıkmadan yakalanır).
        """
        import importlib.util
        import sys

        sys.path.insert(0, str(ROOT))
        try:
            spec = importlib.util.find_spec(
                "src.company_master.etl.scrapers.ostim_detail_scraper"
            )
        finally:
            sys.path.remove(str(ROOT))
        assert spec is not None, (
            "import yolu Python tarafından cozulemiyor; adim 2 her kosumda patlar"
        )
        assert hasattr(spec.loader, "exec_module")

    def test_run_scraper_simge_gercekten_var(self):
        """Hedef modülde `run_scraper` var mı — isim yazım hatası sessiz kalmasın."""
        hedef = (
            ROOT / "src" / "company_master" / "etl" / "scrapers" / "ostim_detail_scraper.py"
        )
        agac = ast.parse(hedef.read_text(encoding="utf-8"))
        adlar = {
            d.name
            for d in ast.walk(agac)
            if isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert "run_scraper" in adlar, f"run_scraper tanimi yok; bulunanlar: {sorted(adlar)}"


# --- Karar 3: restart: "no" ---


class TestKarar3Restart:
    def test_restart_no(self):
        assert _kazima_service().get("restart") == "no", (
            "Batch is; restart on-failure sonsuz dongu (karar 3)"
        )


# --- Kabul 1: scrape_all() hatayi yutmaz, step_scrape() False doner ---


class TestKabul1HataYutuluz:
    def test_scrape_all_donus_tipi_bool(self):
        agac = ast.parse(PIPELINE.read_text(encoding="utf-8"))
        for dugum in ast.walk(agac):
            if isinstance(dugum, ast.FunctionDef) and dugum.name == "scrape_all":
                donus = dugum.returns
                assert donus is not None, "scrape_all() dönüş tipi belirtilmemiş"
                assert getattr(donus, "id", None) == "bool"
                return
        raise AssertionError("scrape_all bulunamadı")

    def test_scrape_all_her_kaynakta_durumu_guncelliyor(self):
        """HER except bloğu `basarili = False` ayarlamalı — kaynak sayısı şansına bağ olmamalı.

        Kırma denemesi notu: yalnız OSTİM bloğundaki atama silindiğinde test
        yeşil kalmıştı, çünkü ASO bloğunda aynı satır duruyordu. Bu, davranışı
        değiştirmese de mandalın bir kaynağı sessizce korumasına izin verirdi
        (D-266). Denetim artık except sayısını ve eşleşmeleri birebir karşılaştırır.
        """
        agac = ast.parse(PIPELINE.read_text(encoding="utf-8"))
        govde = None
        for dugum in ast.walk(agac):
            if isinstance(dugum, ast.FunctionDef) and dugum.name == "scrape_all":
                govde = dugum
                break
        assert govde is not None, "scrape_all bulunamadı"

        except_handlers = [
            dugum
            for dugum in ast.walk(govde)
            if isinstance(dugum, ast.ExceptHandler)
        ]
        assert len(except_handlers) >= 2, (
            f"Kaynak sayisi azalmis gibi: {len(except_handlers)} except blogu. "
            "Her kaynak ayri korunmali."
        )

        atamayan = []
        for handler in except_handlers:
            yanilta_basliyor = False
            for dugum in ast.walk(handler):
                if isinstance(dugum, ast.Assign):
                    for hedef in dugum.targets:
                        if (
                            isinstance(hedef, ast.Name)
                            and hedef.id == "basarili"
                            and isinstance(dugum.value, ast.Constant)
                            and dugum.value.value is False
                        ):
                            yanilta_basliyor = True
            if not yanilta_basliyor:
                atamayan.append(getattr(handler.type, "id", "?"))
        assert not atamayan, (
            f"Bu except blogu hatayi yutuyor (basarili=False atamasi yok): {atamayan}"
        )

    def test_scrape_all_basarisiz_oldugunu_bildiriyor(self):
        govde = _fonksiyon_kaynagi(PIPELINE, "scrape_all")
        assert "except Exception" in govde
        assert "return basarili" in govde, "scrape_all() sonucu geri döndürmüyor"

    def test_scrape_all_yalnizca_tek_kaynak_hatasi_false_doner(self, monkeypatch):
        """Tek kaynak patladığında da False — kaynak sayısına bağlı olmamalı."""
        import sys

        sys.path.insert(0, str(ROOT))
        try:
            from src.company_master.etl import pipeline
        finally:
            sys.path.remove(str(ROOT))

        def patlat(*a, **k):
            raise TimeoutError("kaynak zaman asimi")

        monkeypatch.setattr(pipeline, "_denetim_kaydet", lambda *a, **k: True)
        monkeypatch.setattr(pipeline, "scrape_tum_osb", patlat)
        monkeypatch.setattr(pipeline, "run_full_scrape", lambda *a, **k: None)
        assert pipeline.scrape_all() is False, (
            "OSTIM basarisizken scrape_all() True donuyor"
        )

        monkeypatch.setattr(pipeline, "_denetim_kaydet", lambda *a, **k: True)
        monkeypatch.setattr(pipeline, "scrape_tum_osb", lambda *a, **k: None)
        monkeypatch.setattr(pipeline, "run_full_scrape", patlat)
        assert pipeline.scrape_all() is False, (
            "ASO basarisizken scrape_all() True donuyor"
        )

    def test_step_scrape_donus_degerini_kontrol_eder(self):
        govde = _fonksiyon_kaynagi(REFRESH, "step_scrape")
        assert "scrape_all()" in govde
        assert "basarili = scrape_all()" in govde, (
            "step_scrape() dönüş değerini yok sayıyor; başarısızlıkta da True dönüyor"
        )
        assert "if not basarili" in govde and "return False" in govde

    def test_scrape_all_hata_uretir_ve_false_doner(self, monkeypatch):
        """Entegrasyon kanıtı: kaynak patlayınca scrape_all False dönmeli."""
        import sys

        sys.path.insert(0, str(ROOT))
        try:
            from src.company_master.etl import pipeline
        finally:
            sys.path.remove(str(ROOT))

        def patlat(*a, **k):
            raise TimeoutError("kaynak zaman asimi")

        monkeypatch.setattr(pipeline, "_denetim_kaydet", lambda *a, **k: True)
        monkeypatch.setattr(pipeline, "scrape_tum_osb", patlat)
        monkeypatch.setattr(pipeline, "run_full_scrape", patlat)
        assert pipeline.scrape_all() is False

    def test_scrape_all_hepsi_basarili_ise_true_doner(self, monkeypatch):
        """Kayit ureten iki kaynak icin True.

        Sozlesme genisletildi: hata vermemek yeterli degil, kayit uretmek
        de gerekiyor. OSTIM generator oldugu icin mock iterable dondurmek
        zorunda; ASO ise dosya satir sayisini artirmali.
        """
        import sys

        sys.path.insert(0, str(ROOT))
        try:
            from src.company_master.etl import pipeline
        finally:
            sys.path.remove(str(ROOT))

        monkeypatch.setattr(pipeline, "_denetim_kaydet", lambda *a, **k: True)
        monkeypatch.setattr(pipeline, "scrape_tum_osb", lambda *a, **k: iter([1, 2]))
        monkeypatch.setattr(pipeline, "run_full_scrape", lambda *a, **k: None)
        satirlar = iter([100, 104])
        monkeypatch.setattr(pipeline, "_satir_sayisi", lambda yol: next(satirlar))
        assert pipeline.scrape_all() is True


# --- Kabul 2: update_task_board() kilitsiz pano yazmaz ---


class TestKabul2PanoSsqt:
    def test_update_task_board_fonksiyonu_yok(self):
        """Pano yalnız orkestratör yazar (D-77). Bu betik artık yazmamalı."""
        kaynak = REFRESH.read_text(encoding="utf-8")
        assert "def update_task_board" not in kaynak, (
            "Kilitsiz task_board.json yazımı SSOT riski (kabul 2)"
        )

    def test_task_board_json_yazimi_yok(self):
        """Satır-bazlı tarama (D-322): yorumda geçmesi ihlal değil, kodda geçmesi ihlal.

        Regex tüm dosya metninde arama yapınca açıklama satırlarını da yakalar ve
        yanlış negatif verir. Bu yüzden yorum satırları ayıklanır.
        """
        kod_satirlari = [
            satir
            for satir in REFRESH.read_text(encoding="utf-8").splitlines()
            if satir.strip() and not satir.strip().startswith("#")
        ]
        ihlaller = [s for s in kod_satirlari if "task_board.json" in s]
        assert not ihlaller, f"Kod icinde pano yazimi var: {ihlaller}"

    def test_main_pano_guncellemiyor(self):
        govde = _fonksiyon_kaynagi(REFRESH, "main")
        assert "update_task_board" not in govde

    def test_exit_kodu_basarisizlikta_sifirdan_farkli(self):
        govde = _fonksiyon_kaynagi(REFRESH, "main")
        assert "sys.exit(0 if success else 1)" in govde


# --- Kabul 4: .dockerignore gözden geçirildi ---


class TestKabul4Dockerignore:
    def test_kazima_giris_noktasi_image_disi_degil(self):
        """Entry point `refresh_pipeline.py` — `scripts/_*.py` deseni onu yakalamaz."""
        desenler = [
            satir.strip()
            for satir in (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
            if satir.strip() and not satir.startswith("#")
        ]
        import fnmatch

        giris = "scripts/refresh_pipeline.py"
        assert not any(fnmatch.fnmatch(giris, d) for d in desenler), (
            "Pipeline giriş noktasi image disi kaldi"
        )

    def test_scripts_icin_kanitsiz_istisna_deseni_yok(self):
        """Dışlama kuralı işe yarıyor; gerekirse istisna *kanıtla* açılır.

        Not: `!.env.example` gibi gizli-bilgi istisnaları bu kapsamda değildir —
        yalnız `scripts/_*.py` dışlamasını etkisizleştiren istisna aranır.
        """
        desenler = [
            satir.strip()
            for satir in (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
            if satir.strip().startswith("!")
        ]
        scripts_istisnalari = [d for d in desenler if "scripts" in d]
        assert not scripts_istisnalari, (
            f"Kanıtsiz scripts istisnasi: {scripts_istisnalari}. "
            "Gerekçe kabul 4'te rapora yazılmalı."
        )

    def test_syntax_warning_yok(self):
        """Ertelenen not: refresh_pipeline.py:10 '\\P' SyntaxWarning düzeltildi."""
        import warnings

        with warnings.catch_warnings(record=True) as yakalanan:
            warnings.simplefilter("always")
            ast.parse(REFRESH.read_text(encoding="utf-8"))
        syntax = [w for w in yakalanan if issubclass(w.category, SyntaxWarning)]
        assert not syntax, f"SyntaxWarning kaldi: {[str(w.message) for w in syntax]}"


# --- Bos basari kapisi: kayit uretmeyen kaynak basarili sayilmaz ---


class TestBosBasariKapisi:
    """[1/4] yesil raporlarken OSTIM 0 kayit uretiyordu.

    Kok neden: `scrape_tum_osb` bir generator fonksiyon (yield iceriyor)
    ve `pipeline.py` onu tuketmiyordu. Generator'i cagirmak govdesini
    calistirmaz; hicbir HTTP istegi yapilmaz, robots.txt kontrolu bile
    calismaz ve dosya hic yazilmaz. 0,002 saniyelik "[1/4] OK" tam olarak
    bunun olcumudur.
    """

    def test_generator_tuketiliyor(self):
        kaynak = _fonksiyon_kaynagi(PIPELINE, "scrape_all")
        assert "sum(1 for _ in scrape_tum_osb" in kaynak, (
            "scrape_tum_osb bir generator; tuketilmezse govdesi hic calismaz"
        )

    def test_sifir_kayit_basarisiz_sayilir(self):
        kaynak = _fonksiyon_kaynagi(PIPELINE, "scrape_all")
        assert "ostim_kayit == 0" in kaynak, "OSTIM 0 kayit basarili sayilmamali"
        assert "yeni kayıt üretmedi" in kaynak, "ASO 0 kayit basarili sayilmamali"

    def test_sifir_kayit_false_doner(self, monkeypatch):
        from company_master.etl import pipeline as mod

        monkeypatch.setattr(mod, "_denetim_kaydet", lambda *a, **k: True)
        monkeypatch.setattr(mod, "scrape_tum_osb", lambda output_path: iter(()))
        monkeypatch.setattr(mod, "run_full_scrape", lambda: None)
        monkeypatch.setattr(mod, "_satir_sayisi", lambda yol: 0)

        assert mod.scrape_all() is False, "hicbir kaynak kayit uretmedi ama True dondu"

    def test_kayit_uretilirse_true_doner(self, monkeypatch):
        from company_master.etl import pipeline as mod

        monkeypatch.setattr(mod, "_denetim_kaydet", lambda *a, **k: True)
        monkeypatch.setattr(mod, "scrape_tum_osb", lambda output_path: iter([1, 2, 3]))
        monkeypatch.setattr(mod, "run_full_scrape", lambda: None)
        satirlar = iter([0, 7])
        monkeypatch.setattr(mod, "_satir_sayisi", lambda yol: next(satirlar))

        assert mod.scrape_all() is True


# --- Kabul 3a: pipeline denetim kaydi birakir (D-310 katman 5) ---
# 0050 tablosu + KazimaYazici diskte vardir; EKSIK OLAN pipeline cagrisidi.
# "Goc yazilmamis" teşhisi yanlisti — burdeki testler tam olarak o yanlis
# teşhisin geri donmemisini engeller.


class TestDenetimKaydi:
    @staticmethod
    def _yukle():
        import sys

        sys.path.insert(0, str(ROOT))
        try:
            from src.company_master.etl import pipeline
        finally:
            sys.path.remove(str(ROOT))
        return pipeline

    def test_yazici_modul_diskte_var(self):
        """Denetim yazicisi diskte — yalniz cagirmak eksikti."""
        yol = ROOT / "src/company_master/etl/scrape_kayit.py"
        assert yol.exists(), "scrape_kayit.py yok"
        govde = yol.read_text(encoding="utf-8")
        assert "class KazimaYazici" in govde
        assert "INSERT INTO scrape_audit_log" in govde

    def test_goc_0050_diskte_var(self):
        goc = ROOT / "src/company_master/schema/migrations/0050_scrape_audit_log.sql"
        assert goc.exists(), "0050_scrape_audit_log.sql yok"

    def test_pipeline_denetim_yazicisini_cağirir(self):
        pipeline = self._yukle()
        kaynak = _fonksiyon_kaynagi(
            ROOT / "src/company_master/etl/pipeline.py", "scrape_all"
        )
        assert kaynak.count("_denetim_kaydet") == 2, (
            "scrape_all() iki kaynak icin de denetim kaydi yazmali"
        )
        assert callable(pipeline._denetim_kaydet)

    def test_basarili_kayit_success_yazar(self, monkeypatch):
        pipeline = self._yukle()
        cagrilan = []

        class _Y:
            def __init__(self, kaynak_adi, *, task_id=None):
                self.kaynak_adi = kaynak_adi
                self.task_id = task_id

            def audit_kaydet(self, url, **kw):
                cagrilan.append((self.kaynak_adi, self.task_id, url, kw))
                return 1

        import src.company_master.etl.scrape_kayit as sk

        monkeypatch.setattr(sk, "KazimaYazici", _Y)
        assert pipeline._denetim_kaydet("ostim.org.tr", basarili=True, kayit=12) is True
        kaynak_adi, task_id, url, kw = cagrilan[0]
        assert kaynak_adi == "ostim.org.tr"
        assert task_id == pipeline.TASK_ID
        assert url == "pipeline://ostim.org.tr"
        assert kw["status"] == "success"
        assert kw["bayt"] == 12

    def test_hatali_kayit_error_durumu_yazar(self, monkeypatch):
        pipeline = self._yukle()
        cagrilan = []

        class _Y:
            def __init__(self, kaynak_adi, *, task_id=None):
                pass

            def audit_kaydet(self, url, **kw):
                cagrilan.append(kw)

        import src.company_master.etl.scrape_kayit as sk

        monkeypatch.setattr(sk, "KazimaYazici", _Y)
        assert (
            pipeline._denetim_kaydet(
                "aso.org.tr", basarili=False, kayit=0, hata="0 kayit uretildi"
            )
            is True
        )
        assert cagrilan[0]["status"] == "error"
        assert cagrilan[0]["hata"] == "0 kayit uretildi"

    def test_db_hatasi_yazilirsa_kosu_basarisiz(self, monkeypatch):
        """Denetlenemeyen kosu, denetlenmis basaridan farksiz degildir."""
        pipeline = self._yukle()
        monkeypatch.setattr(pipeline, "scrape_tum_osb", lambda *a, **k: iter([1]))
        monkeypatch.setattr(pipeline, "run_full_scrape", lambda *a, **k: None)
        satirlar = iter([10, 11])
        monkeypatch.setattr(pipeline, "_satir_sayisi", lambda yol: next(satirlar))
        monkeypatch.setattr(pipeline, "_denetim_kaydet", lambda *a, **k: False)
        assert pipeline.scrape_all() is False, (
            "denetim kaydi yazilamayinca kosu True donuyor"
        )

    def test_kayit_yazilamayi_sessizce_gecmiyor(self, monkeypatch, caplog):
        """DB yokken sessiz gecmek hataydi; kayit olmayan kosu olculemez."""
        pipeline = self._yukle()

        def _patlat(*a, **k):
            raise RuntimeError("db yok")

        import src.company_master.etl.scrape_kayit as sk

        monkeypatch.setattr(sk, "KazimaYazici", _patlat)
        with caplog.at_level("ERROR"):
            assert pipeline._denetim_kaydet("ostim.org.tr", basarili=True, kayit=1) is False
        assert any("DENETIM KAYDI YAZILAMADI" in r.message for r in caplog.records), (
            "denetim hatasi loglanmadi"
        )

    def test_her_kaynak_icin_ayri_kayit(self, monkeypatch):
        pipeline = self._yukle()
        cagrilan = []
        monkeypatch.setattr(
            pipeline, "_denetim_kaydet", lambda k, **kw: cagrilan.append(k) or True
        )
        monkeypatch.setattr(pipeline, "scrape_tum_osb", lambda *a, **k: iter([1, 2]))
        monkeypatch.setattr(pipeline, "run_full_scrape", lambda *a, **k: None)
        satirlar = iter([5, 6])
        monkeypatch.setattr(pipeline, "_satir_sayisi", lambda yol: next(satirlar))
        pipeline.scrape_all()
        assert cagrilan == ["ostim.org.tr", "aso.org.tr"]
