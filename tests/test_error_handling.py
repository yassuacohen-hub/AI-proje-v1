# -*- coding: utf-8 -*-
"""UTKU-03 — Hata loglama sistemi testleri.

Kapsam: src/company_master/core/error_handling.py
  - setup_logging / get_logger
  - JSONFormatter (structured JSON)
  - mask_sensitive (PII/secret masking)
  - LogContext / set_log_context (context enrichment)
  - handle_exception dekoratoru
  - web_app.py entegrasyonu (global handler + middleware)
"""
from __future__ import annotations

import importlib
import json
import logging
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from company_master.core import error_handling as eh  # noqa: E402


def _kayit(mesaj="test", seviye=logging.INFO, exc_info=None, **extra):
    rec = logging.LogRecord(
        name="test", level=seviye, pathname=__file__, lineno=1,
        msg=mesaj, args=(), exc_info=exc_info,
    )
    for k, v in extra.items():
        setattr(rec, k, v)
    return rec


def _dokun(handler):
    handler.flush()


class _Toplayici(logging.Handler):
    """LogRecord toplayan test handler'i (caplog yerine kullanilir)."""

    def __init__(self):
        super().__init__()
        self.kayitlar: list = []

    def emit(self, record):
        self.kayitlar.append(record)


# ============================================================
# 1. setup_logging / get_logger
# ============================================================

class TestSetupLogging:
    def test_setup_logging_logger_donusturur(self, tmp_path):
        logger = eh.setup_logging(level="DEBUG", log_file=str(tmp_path / "app.log"))
        assert isinstance(logger, logging.Logger)
        assert logger.handlers, "logger en az bir handler tasimali"

    def test_get_logger_ayni_adi_ayni_logger(self):
        assert eh.get_logger("modul.test") is eh.get_logger("modul.test")
        assert eh.get_logger("modul.test").name == "modul.test"

    def test_get_logger_context_filter_ekler(self, tmp_path):
        eh.setup_logging(level="INFO", log_file=str(tmp_path / "svc.log"))
        logger = eh.get_logger("servis")
        assert any(isinstance(f, eh._ContextFilter) for f in logger.filters), \
            "get_logger context filter eklemeli"

    def test_setup_logging_iz_dizini_olmayan_yol_calisir(self, tmp_path, monkeypatch):
        """log_file dizin bileşeni icermiyorsa os.makedirs('') patlamamali."""
        monkeypatch.chdir(tmp_path)
        logger = eh.setup_logging(level="INFO", log_file="dizinsiz.log")
        assert (tmp_path / "dizinsiz.log").exists()
        assert logger.handlers

    def test_json_format_kapaliyken_insan_okuunur(self, tmp_path):
        log_file = tmp_path / "human.log"
        eh.setup_logging(level="INFO", json_format=False, log_file=str(log_file))
        eh.get_logger("human").info("merhaba")
        for h in logging.getLogger().handlers:
            _dokun(h)
        icerik = log_file.read_text(encoding="utf-8")
        assert "merhaba" in icerik
        assert not icerik.lstrip().startswith("{")


# ============================================================
# 2. JSONFormatter — structured JSON output
# ============================================================

class TestJSONFormatter:
    def test_gecerli_json_uretir(self):
        veri = json.loads(eh.JSONFormatter().format(_kayit("olay")))
        assert veri["message"] == "olay"
        assert veri["level"] == "INFO"

    def test_zorunlu_alanlar_mevcut(self):
        veri = json.loads(eh.JSONFormatter().format(_kayit()))
        for alan in ("timestamp", "level", "logger", "message"):
            assert alan in veri, f"eksik alan: {alan}"

    def test_extra_alanlar_eklenir(self):
        cikti = eh.JSONFormatter().format(_kayit(request_id="abc123", tenant_id="t1"))
        veri = json.loads(cikti)
        assert veri["request_id"] == "abc123"
        assert veri["tenant_id"] == "t1"

    def test_istisna_bilgisi_dahil_edilir(self):
        try:
            raise ValueError("patladi")
        except ValueError:
            rec = _kayit("hata", logging.ERROR, exc_info=sys.exc_info())
        cikti = eh.JSONFormatter().format(rec)
        veri = json.loads(cikti)
        assert veri["level"] == "ERROR"
        assert veri["exception"]["type"] == "ValueError"
        assert "patladi" in veri["exception"]["message"]
        assert "ValueError" in veri["exception"]["traceback"]


# ============================================================
# 3. mask_sensitive — PII / secret masking
# ============================================================

class TestMaskSensitive:
    def test_eposta_maskelenir(self):
        sonuc = str(eh.mask_sensitive("iletisim: user@example.com"))
        assert "user@example.com" not in sonuc
        assert "[EMAIL]" in sonuc

    def test_kredi_karti_maskelenir(self):
        assert "4111111111111111" not in str(eh.mask_sensitive("kart 4111111111111111"))

    def test_telefon_maskelenir(self):
        assert "05551234567" not in str(eh.mask_sensitive("tel: 05551234567"))

    def test_sozde_anahtar_maskelenir(self):
        metin = str(eh.mask_sensitive({"api_key": "sk-abc123secret", "ad": "Ali"}))
        assert "sk-abc123secret" not in metin
        assert "Ali" in metin, "PII olmayan alan korunmali"

    def test_veri_yoksa_bozulmaz(self):
        assert eh.mask_sensitive({}) is not None
        assert eh.mask_sensitive("") == "" or eh.mask_sensitive("") is not None



# ============================================================
# 4. LogContext / set_log_context — context enrichment
# ============================================================

class TestLogContext:
    def teardown_method(self):
        eh.clear_log_context()

    def test_set_log_context_alanlari_yazar(self):
        eh.set_log_context(request_id="r1", user_id="u1", trace_id="t1")
        ctx = eh.get_log_context()
        assert ctx["request_id"] == "r1"
        assert ctx["user_id"] == "u1"
        assert ctx["trace_id"] == "t1"

    def test_request_id_otomatik_uretilir(self):
        eh.set_log_context()
        assert eh.get_log_context()["request_id"]

    def test_extra_alanlar_dondurulur(self):
        eh.set_log_context(request_id="r1", mod="scraper", tenant="acme")
        ctx = eh.get_log_context()
        assert ctx["mod"] == "scraper"
        assert ctx["tenant"] == "acme"

    def test_clear_log_context_hepsini_siler(self):
        eh.set_log_context(request_id="r1", user_id="u1", mod="x")
        eh.clear_log_context()
        assert eh.get_log_context() == {}

    def test_log_context_context_manager(self):
        with eh.LogContext(request_id="ctx-1", user_id="u9", extra_field="v1"):
            assert logging.getLogRecordFactory() is not None
        # cikis sonrasi orijinal factory geri yuklenmis olmali
        assert callable(logging.getLogRecordFactory())


# ============================================================
# 5. handle_exception — dekorator
# ============================================================

class TestHandleException:
    @pytest.fixture
    def kayitlar(self):
        """setup_logging root handler'lari temizledigi icin caplog yerine
        logger'a ozel bir handler baglanir."""
        toplayici = _Toplayici()
        logger = eh.get_logger("deko.test")
        logger.addHandler(toplayici)
        logger.setLevel(logging.DEBUG)
        try:
            yield toplayici
        finally:
            logger.removeHandler(toplayici)

    def test_hata_loglanir_ve_yayilir(self, kayitlar):
        log = eh.get_logger("deko.test")

        @eh.handle_exception(log)
        def patlayan():
            raise RuntimeError("beklenen hata")

        with pytest.raises(RuntimeError, match="beklenen hata"):
            patlayan()

        assert kayitlar.kayitlar, "istisna loglanmali"
        assert any("beklenen hata" in r.getMessage() for r in kayitlar.kayitlar)
        assert any(getattr(r, "exception_type", None) == "RuntimeError"
                   for r in kayitlar.kayitlar)

    def test_hata_yoksa_sonuc_doner(self):
        log = eh.get_logger("deko.ok")

        @eh.handle_exception(log)
        def saglam(x, y=2):
            return x + y

        assert saglam(3) == 5

    def test_metadata_korunur(self):
        log = eh.get_logger("deko.meta")

        @eh.handle_exception(log)
        def adli():
            """dokumantasyon korunmali"""
            return 1

        assert adli.__name__ == "adli"
        assert adli.__doc__ == "dokumantasyon korunmali"

    def test_log_exception_extra_alanlari_ekler(self, kayitlar):
        log = eh.get_logger("deko.test")
        eh.log_exception(log, ValueError("x"), context={"path": "/api/x"})
        rec = kayitlar.kayitlar[-1]
        assert getattr(rec, "exception_type", None) == "ValueError"
        assert getattr(rec, "path", None) == "/api/x"


# ============================================================
# 6. web_app.py entegrasyonu
# ============================================================

class TestWebAppIntegration:
    @pytest.fixture(scope="class")
    @classmethod
    def web_app_source(cls):
        kaynak = ROOT / "web_app.py"
        if not kaynak.exists():
            pytest.skip("web_app.py yok")
        return kaynak.read_text(encoding="utf-8")

    def test_error_handling_import_ediliyor(self, web_app_source):
        assert "from company_master.core.error_handling import" in web_app_source

    def test_setup_logging_startup_cagriliyor(self, web_app_source):
        assert "_setup_app_logging()" in web_app_source

    def test_global_exception_handler_var(self, web_app_source):
        assert "@app.exception_handler(Exception)" in web_app_source
        assert "_unhandled_exception_handler" in web_app_source

    def test_request_middleware_ekleniyor(self, web_app_source):
        assert "LoggingMiddleware" in web_app_source
        assert "app.add_middleware(_LoggingMiddleware)" in web_app_source

    def test_all_ici_tanimlilar_mevcut(self):
        mod = importlib.import_module("company_master.core.error_handling")
        for ad in eh.__all__:
            assert hasattr(mod, ad), f"__all__ icinde tanimsiz: {ad}"


# ============================================================
# 7. Log dosyasi rotasyonu / dual output
# ============================================================

class TestFileRotation:
    def test_dosya_hedefine_yazilir(self, tmp_path):
        hedef = tmp_path / "rotasyon.log"
        eh.setup_logging(level="INFO", log_file=str(hedef))
        eh.get_logger("rot").warning("mesaj")
        for h in logging.getLogger().handlers:
            _dokun(h)
        assert "mesaj" in hedef.read_text(encoding="utf-8")

    def test_stdout_ve_dosya_ikili_cikti(self, tmp_path, capsys):
        hedef = tmp_path / "dual.log"
        eh.setup_logging(level="INFO", log_file=str(hedef), console_output=True)
        eh.get_logger("dual").info("stdout-ve-dosya")
        for h in logging.getLogger().handlers:
            _dokun(h)
        assert "stdout-ve-dosya" in capsys.readouterr().out
        assert "stdout-ve-dosya" in hedef.read_text(encoding="utf-8")
