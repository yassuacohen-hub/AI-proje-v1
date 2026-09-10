# -*- coding: utf-8 -*-
"""SEC-01 — API Güvenlik Regresyonu testleri.

Kapsam:
- require_admin fail-closed (DASH_API_KEY tanımlı değilken yönetici erişimi kapalı).
- /api/companies/export çoklu kaynak SQL üretimi (bozuk IN ifadesi düzeltmesi).

Bu testler DB bağımsızdır; canlı veritabanı bağlantısı gerektirmez.
Calistirma: python -m pytest tests/test_security_regresyon.py -v
"""
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import web_app
from web_app import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ── require_admin fail-closed ────────────────────────────────────────────
class TestRequireAdminFailClosed:
    def test_key_tanimli_degilse_erisim_reddedilir(self, monkeypatch):
        """Bos DASH_API_KEY + kimlik bilgisi yok -> 403 (fail-closed)."""
        monkeypatch.setenv("DASH_API_KEY", "")
        with pytest.raises(HTTPException) as ei:
            web_app.require_admin(authorization=None, x_api_key=None, api_key="")
        assert ei.value.status_code == 403

    def test_bos_key_query_param_reddedilir(self, monkeypatch):
        """Bos DASH_API_KEY + bos api_key parametresi -> 403."""
        monkeypatch.setenv("DASH_API_KEY", "")
        with pytest.raises(HTTPException) as ei:
            web_app.require_admin(authorization=None, x_api_key=None, api_key="")
        assert ei.value.status_code == 403

    def test_yanlis_key_reddedilir(self, monkeypatch):
        monkeypatch.setenv("DASH_API_KEY", "gercek-anahtar")
        with pytest.raises(HTTPException) as ei:
            web_app.require_admin(authorization=None, x_api_key="yanlis", api_key="")
        assert ei.value.status_code == 403

    def test_dogru_key_kabul_edilir(self, monkeypatch):
        monkeypatch.setenv("DASH_API_KEY", "gercek-anahtar")
        sonuc = web_app.require_admin(authorization=None, x_api_key="gercek-anahtar", api_key="")
        assert sonuc == "admin-key"

    def test_dogru_key_query_param_kabul_edilir(self, monkeypatch):
        monkeypatch.setenv("DASH_API_KEY", "gercek-anahtar")
        sonuc = web_app.require_admin(authorization=None, x_api_key=None, api_key="gercek-anahtar")
        assert sonuc == "admin-key"

    def test_api_key_tanimli_degilken_admin_endpoint_403(self, client, monkeypatch):
        """End-to-end: DASH_API_KEY yokken /api/admin/pending -> 403 (DB'ye dokunmadan)."""
        monkeypatch.setenv("DASH_API_KEY", "")
        r = client.get("/api/admin/pending")
        assert r.status_code == 403


# ── CSV export çoklu kaynak SQL ──────────────────────────────────────────
class _FakeResult:
    def mappings(self):
        return self

    def all(self):
        return []


class _FakeConn:
    def __init__(self):
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, stmt, *args, **kwargs):
        self.executed.append((str(stmt), args, kwargs))
        return _FakeResult()


class _FakeEngine:
    def __init__(self):
        self.conn = _FakeConn()

    def connect(self):
        return self.conn


class TestCsvExportMultiSourceSql:
    def test_coklu_kaynak_ic_okuyan_sql_uretir(self, monkeypatch):
        engine = _FakeEngine()
        monkeypatch.setattr(web_app, "get_engine", lambda: engine)

        resp = web_app.api_companies_export(
            format="csv", sources="ostim,aso", mask=1, _auth="test"
        )
        assert resp.status_code == 200

        sql, args, _kwargs = engine.conn.executed[0]
        params = args[0] if args else {}
        assert "s.source_name IN (:src_0, :src_1)" in sql
        assert "join(placeholders)" not in sql  # eski bozuk desen yok
        assert params["src_0"] == "ostim"
        assert params["src_1"] == "aso"

    def test_tek_kaynak_esitlik_kullanir(self, monkeypatch):
        engine = _FakeEngine()
        monkeypatch.setattr(web_app, "get_engine", lambda: engine)

        resp = web_app.api_companies_export(
            format="csv", sources="ostim", mask=1, _auth="test"
        )
        assert resp.status_code == 200

        sql, args, _kwargs = engine.conn.executed[0]
        params = args[0] if args else {}
        assert "s.source_name = :source_name" in sql
        assert params["source_name"] == "ostim"
# ── SEC-02: TLS dogrulama regresyonu ─────────────────────────────────────
class TestTlsVerificationRegresyon:
    def test_job_postings_scraper_verify_false_kaldirildi(self, monkeypatch):
        """fetch_page requests.get'i verify=False olmadan cagirmali (TLS default True)."""
        import src.company_master.etl.job_postings_scraper as jps

        captured: dict = {}

        class FakeResp:
            status_code = 200
            text = "<html>test</html>"
            apparent_encoding = "utf-8"

            def raise_for_status(self):
                pass

        def fake_get(self, url, **kwargs):
            captured["url"] = url
            captured["kwargs"] = kwargs
            return FakeResp()

        monkeypatch.setattr(jps.requests.Session, "get", fake_get)
        jps.fetch_page("https://ornek.com/kariyer")
        assert captured["url"] == "https://ornek.com/kariyer"
        assert captured["kwargs"].get("verify", True) is not False

    def test_verify_false_kaynak_kodda_yok_security_kapsami(self):
        """SEC-02 kapsamindaki dosyalarda verify=False kalintisi olmamali (statik)."""
        hedefler = [
            ROOT / "src" / "company_master" / "etl" / "job_postings_scraper.py",
            ROOT / "scripts" / "p32_vkn_from_ivedik_baskent.py",
        ]
        for dosya in hedefler:
            icerik = dosya.read_text(encoding="utf-8-sig", errors="ignore")
            # Yorum satirlarini sayma: satir basindaki # karakterini yoksay.
            kod = [ln for ln in icerik.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
            tum = "\n".join(kod)
            assert "verify=False" not in tum, f"{dosya.name} icinde verify=False kaldi"

    def test_permission_router_policy_for_dinamik_domain(self):
        """SEC-02: policy_for bilinmeyen domain icin default SourcePolicy uretir."""
        from company_master.utils.scraping_permission_router import get_router

        router = get_router()
        p = router.policy_for("dinamik-firma.com.tr")
        assert p.domain == "dinamik-firma.com.tr"
        assert p.kvkk_safe is False  # kayitli degil -> default guvenli degil
        assert p.respect_robots is True  # robots.txt yine de uygulanir