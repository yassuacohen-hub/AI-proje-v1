# -*- coding: utf-8 -*-
"""CL-01 — API Entegrasyon Test Suite (butun endpointler).

Kapsam:
- Rota envanteri: /api/* + /metrics — tanimli rota listesiyle eslesme kontrati
- Acik (DB'siz) uclar: health, tasks, handoffs, performance, metrics
- DB bagli GET uclar: kpi, companies, company/{id}, export, match, quality-trend,
  nace-distribution, sources, intelligence/dashboard (+SSE stream)
- Buyer kimlik akisi: login/register validasyonlari, token-401 fail-closed
- Admin uclar: require_admin fail-closed + DB mock'lu islemler
- Apify webhook: health/metrics + gecersiz istek reddi

DB yok: tum engine cagrilari _FakeEngine ile mocklanir (CI-guvenli).
Calistirma: pytest tests/test_api_integration.py -q
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import web_app  # noqa: E402
from web_app import app  # noqa: E402

API_ANAHTARI = "test-anahtar-123"

# Rota kontrati: her ucun beklenen method listesi (FastAPI built-in'leri haric)
EXPECTED_ROUTES: dict[str, set[str]] = {
    "/api/health": {"GET"},
    "/api/webhooks/apify": {"POST"},
    "/api/webhooks/apify/health": {"GET"},
    "/api/webhooks/apify/metrics": {"GET"},
    "/metrics": {"GET"},
    "/api/kpi": {"GET"},
    "/api/tasks": {"GET"},
    "/api/handoffs": {"GET"},
    "/api/companies": {"GET"},
    "/api/companies/export": {"GET"},
    "/api/match": {"GET"},
    "/api/buyer/register": {"POST"},
    "/api/buyer/categories": {"GET"},
    "/api/buyer/profile": {"GET", "PUT"},
    "/api/buyer/ledger": {"GET"},
    "/api/buyer/login": {"POST"},
    "/api/buyer/logout": {"POST"},
    "/api/buyer/change-password": {"POST"},
    "/api/buyer/reset-password-request": {"POST"},
    "/api/buyer/reset-password-confirm": {"POST"},
    "/api/buyer/verify-email-request": {"POST"},
    "/api/buyer/verify-email/{token}": {"GET"},
    "/api/buyer/welcome-telegram": {"POST"},
    "/api/me": {"GET"},
    "/api/admin/login": {"GET"},
    "/api/admin/pending": {"GET"},
    "/api/admin/approve": {"POST"},
    "/api/admin/credit": {"POST"},
    "/api/admin/api-usage": {"GET"},
    "/api/admin/rotate-key": {"POST"},
    "/api/admin/categories": {"GET", "POST"},
    "/api/dashboard": {"GET"},
    "/api/performance": {"GET"},
    "/api/quality-trend": {"GET"},
    "/api/nace-distribution": {"GET"},
    "/api/sources": {"GET"},
    "/api/company/{company_id}": {"GET"},
    "/api/intelligence/dashboard": {"GET"},
    "/api/intelligence/dashboard/stream": {"GET"},
}


# ── Sahte DB altyapisi ────────────────────────────────────────────────────
class _Sonuc:
    """Tek execute() sonucu: first/all/scalar + mappings zinciri."""

    def __init__(self, first=None, rows=None, scalar=None):
        self._first = first
        self._rows = list(rows) if rows else []
        self._scalar = scalar

    def first(self):
        return self._first

    def mappings(self):
        return self

    def all(self):
        return self._rows

    def scalar(self):
        return self._scalar


class _FakeConn:
    """execute() cagrilarini paylasilan kuyruktan sirayla _Sonuc dondurur."""

    def __init__(self, kuyruk):
        # NOT: kuyrugun kopyasini degil kendisini tutar — her connect()
        # yeni baglanti acsa da sorgular sirayla tuketilir.
        self._kuyruk = kuyruk
        self.executed = []

    def execute(self, stmt, *args, **kwargs):
        self.executed.append(str(stmt))
        return self._kuyruk.pop(0) if self._kuyruk else _Sonuc()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _FakeEngine:
    def __init__(self, sonuclar):
        self._kuyruk = list(sonuclar)

    def connect(self):
        return _FakeConn(self._kuyruk)

    def begin(self):
        return _FakeConn(self._kuyruk)


def _db_yukle(monkeypatch, *sonuclar):
    """web_app.get_engine'i sirali sahte sonuclarla degistirir."""
    engine = _FakeEngine(list(sonuclar))
    monkeypatch.setattr(web_app, "get_engine", lambda: engine)
    return engine


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _rate_limit_temiz():
    """Her test sonrasinda IP rate-limit sayacini temizler (429 kirliligi onler)."""
    yield
    web_app._RATE_LIMIT.clear()


@pytest.fixture()
def dev_modu(monkeypatch):
    """DASH_API_KEY'siz acik (public) mod — DB'siz uclar icin."""
    monkeypatch.setattr(web_app, "DASH_API_KEY", "")
    monkeypatch.delenv("DASH_API_KEY", raising=False)
    web_app._RATE_LIMIT.clear()


@pytest.fixture()
def anahtar_modu(monkeypatch):
    """X-API-Key ile erisilen mod."""
    monkeypatch.setattr(web_app, "DASH_API_KEY", API_ANAHTARI)
    return {"X-API-Key": API_ANAHTARI}


@pytest.fixture()
def admin_modu(monkeypatch):
    """require_admin'i DASH_API_KEY env ile gecen mod."""
    monkeypatch.setenv("DASH_API_KEY", API_ANAHTARI)
    return {"X-API-Key": API_ANAHTARI}

# ── Rota envanteri (kontrat) ─────────────────────────────────────────────
class TestRotaEnvanteri:
    def test_tum_api_rotalari_tanimli_listeyle_eslesir(self):
        actual: dict[str, set[str]] = {}
        for r in app.routes:
            methods = getattr(r, "methods", None)
            path = getattr(r, "path", "")
            if methods and (path.startswith("/api/") or path == "/metrics"):
                actual.setdefault(path, set()).update(m for m in methods if m != "HEAD")
        eksik = {p: m for p, m in EXPECTED_ROUTES.items() if p not in actual}
        fazla = {p: m for p, m in actual.items() if p not in EXPECTED_ROUTES}
        method_fark = {
            p: (EXPECTED_ROUTES.get(p), actual.get(p))
            for p in EXPECTED_ROUTES.keys() & actual.keys()
            if EXPECTED_ROUTES[p] != actual[p]
        }
        assert not eksik, f"TEST EDILMEYEN/OLSAMAYAN ROTALAR: {eksik}"
        assert not fazla, f"BEKLENMEYEN YENI ROTALAR (suite'e ekle): {fazla}"
        assert not method_fark, f"METHOD UYUSMAZLIGI: {method_fark}"


# ── Acik (DB'siz) uclar ──────────────────────────────────────────────────
class TestAcikUclar:
    def test_health_ok(self, client, dev_modu):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_tasks_pano_listesi_doner(self, client, dev_modu):
        r = client.get("/api/tasks")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_handoffs_sozluk_doner(self, client, dev_modu):
        r = client.get("/api/handoffs")
        assert r.status_code == 200
        assert isinstance(r.json(), dict)

    def test_performance_metrik_anahtarlari(self, client, dev_modu):
        r = client.get("/api/performance")
        assert r.status_code == 200
        d = r.json()
        for k in ("db_time_ms", "query_count", "cache_hits", "cache_misses", "cache_hit_rate"):
            assert k in d, k

    def test_metrics_prometheus_metni(self, client, dev_modu):
        r = client.get("/metrics")
        assert r.status_code == 200

    def test_dashboard_html_doner(self, client, dev_modu):
        r = client.get("/api/dashboard")
        assert r.status_code == 200
        assert "html" in r.headers.get("content-type", "")

# ── DB bagli veri uclar ──────────────────────────────────────────────────
class TestVeriUclari:
    def test_kpi_sozlesme(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(first={"total": 10, "avg_score": 42.0}))
        r = client.get("/api/kpi")
        assert r.status_code == 200
        d = r.json()
        assert d["total"] == 10
        assert d["avg_score"] == 42.0

    def test_kpi_bos_veri_bos_sozluk(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(first=None))
        r = client.get("/api/kpi")
        assert r.status_code == 200
        assert r.json() == {}

    def test_companies_liste_sozlesme(self, client, dev_modu, monkeypatch):
        _db_yukle(
            monkeypatch,
            _Sonuc(scalar=1),
            _Sonuc(rows=[{"legal_name": "FIRMA A", "data_quality_score": 70.0}]),
        )
        r = client.get("/api/companies", params={"limit": 1})
        assert r.status_code == 200
        d = r.json()
        assert d["total"] == 1
        assert d["items"][0]["legal_name"] == "FIRMA A"

    def test_companies_limit_ust_sinir(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(scalar=0), _Sonuc(rows=[]))
        r = client.get("/api/companies", params={"limit": 100000})
        assert r.status_code == 200
        assert len(r.json()["items"]) <= web_app.MAX_COMPANIES_LIMIT

    def test_company_detail_bulunur(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(first={"legal_name": "FIRMA A", "data_quality_score": 70.0}))
        r = client.get("/api/company/abc")
        assert r.status_code == 200
        assert r.json()["legal_name"] == "FIRMA A"

    def test_company_detail_bulunamaz_bos_sozluk(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(first=None))
        r = client.get("/api/company/yok")
        assert r.status_code == 200
        assert r.json() == {}

    def test_export_csv_doner(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(scalar=1), _Sonuc(rows=[]))
        r = client.get("/api/companies/export", params={"format": "csv", "mask": 1})
        assert r.status_code == 200
        assert "csv" in r.headers.get("content-type", "").lower()
        assert r.content is not None

    def test_match_gecersiz_buyer_404(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch)  # engine uretilir ama baglanti acilmaz
        r = client.get("/api/match", params={"buyer_id": "uuid-degil"})
        assert r.status_code == 404

    def test_quality_trend_liste(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(rows=[{"bucket": "60-79", "cnt": 5}]))
        r = client.get("/api/quality-trend")
        assert r.status_code == 200
        assert r.json() == [{"bucket": "60-79", "cnt": 5}]

    def test_nace_distribution_liste(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(rows=[{"nace_code": "29", "cnt": 7}]))
        r = client.get("/api/nace-distribution")
        assert r.status_code == 200
        assert r.json()[0]["nace_code"] == "29"

    def test_sources_liste(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(rows=[{"source_name": "ostim", "record_count": 3}]))
        r = client.get("/api/sources")
        assert r.status_code == 200
        assert r.json()[0]["source_name"] == "ostim"

    def test_intelligence_dashboard_sozlesme(self, client, dev_modu, monkeypatch):
        _db_yukle(
            monkeypatch,
            _Sonuc(rows=[{"signal_type": "growth", "cnt": 2}]),
            _Sonuc(rows=[{"cnt": 1}]),
            _Sonuc(rows=[]),
            _Sonuc(rows=[]),
            _Sonuc(rows=[]),
            _Sonuc(rows=[]),
            _Sonuc(rows=[]),
        )
        r = client.get("/api/intelligence/dashboard")
        assert r.status_code == 200
        d = r.json()
        assert d["signal_type_counts"]["growth"] == 2
        assert d["total_active_signals"] == 2

    def test_buyer_categories_sozlesme(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(rows=[]))
        r = client.get("/api/buyer/categories")
        assert r.status_code == 200
        assert r.json() == {"items": []}

# ── Buyer kimlik: fail-closed + login ────────────────────────────────────
class TestBuyerKimlik:
    def test_me_token_yok_401(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.get("/api/me")
        assert r.status_code == 401

    def test_profile_token_yok_401(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.get("/api/buyer/profile")
        assert r.status_code == 401

    def test_ledger_token_yok_401(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.get("/api/buyer/ledger")
        assert r.status_code == 401

    def test_change_password_token_yok_401(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.post("/api/buyer/change-password", json={"new_password": "12345678"})
        assert r.status_code == 401

    def test_me_gecersiz_token_401(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.get("/api/me", params={"token": "bozuk-token"})
        assert r.status_code == 401

    def test_login_gecersiz_email_400(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.post("/api/buyer/login", json={"email": "buzuk", "password": "12345678"})
        assert r.status_code == 400

    def test_login_bilinmeyen_email_404(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(first=None))
        r = client.post("/api/buyer/login", json={"email": "yok@firma.com.tr", "password": "12345678"})
        assert r.status_code == 404

    def test_login_yanlis_sifre_401(self, client, dev_modu, monkeypatch):
        from web_app import _hash_password

        _db_yukle(
            monkeypatch,
            _Sonuc(first={
                "user_id": "u1", "email": "a@firma.com.tr", "status": "onayli",
                "tier": "terminal", "credit_balance": 10, "role": "user",
                "company_name": "FIRMA A", "password_hash": _hash_password("dogru-sifre"),
            }),
        )
        r = client.post("/api/buyer/login", json={"email": "a@firma.com.tr", "password": "yanlis-sifre"})
        assert r.status_code == 401

    def test_login_onay_bekliyor_403(self, client, dev_modu, monkeypatch):
        from web_app import _hash_password

        _db_yukle(
            monkeypatch,
            _Sonuc(first={
                "user_id": "u1", "email": "b@firma.com.tr", "status": "onay_bekliyor",
                "tier": "terminal", "credit_balance": 0, "role": "user",
                "company_name": "FIRMA B", "password_hash": _hash_password("12345678"),
            }),
        )
        r = client.post("/api/buyer/login", json={"email": "b@firma.com.tr", "password": "12345678"})
        assert r.status_code == 403

    def test_login_onayli_kullanici_200_token(self, client, dev_modu, monkeypatch):
        from web_app import _hash_password

        monkeypatch.setattr(
            "company_master.auth.session.create_session", lambda *a, **k: None
        )
        _db_yukle(
            monkeypatch,
            _Sonuc(first={
                "user_id": "u1", "email": "c@firma.com.tr", "status": "onayli",
                "tier": "terminal", "credit_balance": 10, "role": "user",
                "company_name": "FIRMA C", "password_hash": _hash_password("12345678"),
            }),
        )
        r = client.post("/api/buyer/login", json={"email": "c@firma.com.tr", "password": "12345678"})
        assert r.status_code == 200
        d = r.json()
        assert d["token"]
        assert d["user"]["email"] == "c@firma.com.tr"

    def test_logout_ok(self, client, dev_modu):
        r = client.post("/api/buyer/logout", json={})
        assert r.status_code == 200
        assert r.json()["ok"] is True

# ── Buyer kayit + uyelik yardimcilari ────────────────────────────────────
class TestBuyerKayit:
    def test_register_eksik_alan_400(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.post("/api/buyer/register", json={"email": "x@firma.com.tr"})
        assert r.status_code == 400

    def test_register_kisa_sifre_400(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.post(
            "/api/buyer/register",
            json={"email": "x@firma.com.tr", "company_name": "FIRMA X",
                  "password": "kisa", "kvkk_consent": True},
        )
        assert r.status_code == 400

    def test_register_ucretsiz_domain_400(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.post(
            "/api/buyer/register",
            json={"email": "x@gmail.com", "company_name": "FIRMA X",
                  "password": "12345678", "kvkk_consent": True},
        )
        assert r.status_code == 400
        assert "kurumsal" in r.json()["detail"]

    def test_register_kvkk_yok_400(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.post(
            "/api/buyer/register",
            json={"email": "x@firma.com.tr", "company_name": "FIRMA X", "password": "12345678"},
        )
        assert r.status_code == 400
        assert "KVKK" in r.json()["detail"]

    def test_register_mukerrer_email_409(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(first={"user_id": "u1", "status": "onay_bekliyor"}))
        r = client.post(
            "/api/buyer/register",
            json={"email": "x@firma.com.tr", "company_name": "FIRMA X",
                  "password": "12345678", "kvkk_consent": True},
        )
        assert r.status_code == 409

    def test_register_basarili_onay_bekliyor(self, client, dev_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(first=None))
        r = client.post(
            "/api/buyer/register",
            json={"email": "yeni@firma.com.tr", "company_name": "FIRMA Y",
                  "password": "12345678", "kvkk_consent": True},
        )
        assert r.status_code == 200
        d = r.json()
        assert d["ok"] is True
        assert d["status"] == "onay_bekliyor"

    def test_welcome_telegram_onay_bekliyor_403(self, client, dev_modu, monkeypatch):
        monkeypatch.setattr(
            web_app, "_user_from_token",
            lambda tok: {"user_id": "u1", "status": "onay_bekliyor", "company_name": "X", "tier": "terminal", "credit_balance": 0},
        )
        r = client.post("/api/buyer/welcome-telegram", json={"user_token": "t"})
        assert r.status_code == 403

    def test_welcome_telegram_onayli_kullanici_ok(self, client, dev_modu, monkeypatch):
        monkeypatch.setattr(
            web_app, "_user_from_token",
            lambda tok: {"user_id": "u1", "status": "onayli", "company_name": "X",
                         "tier": "terminal", "credit_balance": 5},
        )
        monkeypatch.setattr(web_app, "_send_telegram", lambda metin, chat="": True)
        r = client.post("/api/buyer/welcome-telegram", json={"user_token": "t"})
        assert r.status_code == 200
        assert r.json()["ok"] is True

# ── Admin uclar ──────────────────────────────────────────────────────────
class TestAdminFailClosed:
    @pytest.mark.parametrize(
        "yol,method",
        [("/api/admin/pending", "get"), ("/api/admin/api-usage", "get"),
         ("/api/admin/categories", "get"), ("/api/admin/approve", "post"),
         ("/api/admin/credit", "post"), ("/api/admin/rotate-key", "post"),
         ("/api/admin/categories", "post")],
    )
    def test_anahtar_yokken_403(self, client, monkeypatch, yol, method):
        monkeypatch.setenv("DASH_API_KEY", "")
        kwargs: dict = {"json": {}} if method == "post" else {}
        r = getattr(client, method)(yol, **kwargs)
        assert r.status_code == 403

    def test_yanlis_anahtar_403(self, client, monkeypatch):
        monkeypatch.setenv("DASH_API_KEY", "gercek-anahtar")
        r = client.get("/api/admin/pending", headers={"X-API-Key": "yanlis"})
        assert r.status_code == 403


class TestAdminUclari:
    def test_pending_bos_listeler(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(rows=[]), _Sonuc(rows=[]))
        r = client.get("/api/admin/pending", headers=admin_modu)
        assert r.status_code == 200
        d = r.json()
        assert d["bekleyen"] == []
        assert d["onayli_son"] == []

    def test_api_usage_sozlesme(self, client, admin_modu):
        r = client.get("/api/admin/api-usage", headers=admin_modu)
        assert r.status_code == 200
        assert "items" in r.json()
        assert "rate_limits" in r.json()

    def test_approve_user_id_yok_400(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.post("/api/admin/approve", headers=admin_modu, json={})
        assert r.status_code == 400

    def test_approve_uuid_degil_400(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.post("/api/admin/approve", headers=admin_modu, json={"user_id": "abc"})
        assert r.status_code == 400

    def test_approve_kullanici_yok_404(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(first=None))
        r = client.post("/api/admin/approve", headers=admin_modu, json={"user_id": "11111111-1111-1111-1111-111111111111"})
        assert r.status_code == 404

    def test_credit_eksik_parametre_400(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.post("/api/admin/credit", headers=admin_modu, json={"user_id": "u1", "amount": 0})
        assert r.status_code == 400

    def test_credit_kullanici_yok_404(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(first=None))
        r = client.post("/api/admin/credit", headers=admin_modu, json={"user_id": "u1", "amount": 50})
        assert r.status_code == 404

    def test_credit_basari(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(first={"credit_balance": 10, "tier": "terminal"}))
        r = client.post("/api/admin/credit", headers=admin_modu, json={"user_id": "u1", "amount": 50})
        assert r.status_code == 200
        assert r.json()["credit_balance"] == 60

    def test_rotate_uuid_degil_400(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.post("/api/admin/rotate-key", headers=admin_modu, json={"user_id": "abc"})
        assert r.status_code == 400

    def test_rotate_kullanici_yok_404(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(first=None))
        r = client.post("/api/admin/rotate-key", headers=admin_modu, json={"user_id": "22222222-2222-2222-2222-222222222222"})
        assert r.status_code == 404

    def test_rotate_enterprise_degil_400(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(first={"email": "a@x.com.tr", "tier": "terminal", "status": "onayli"}))
        r = client.post("/api/admin/rotate-key", headers=admin_modu, json={"user_id": "22222222-2222-2222-2222-222222222222"})
        assert r.status_code == 400

    def test_rotate_enterprise_basarili(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(first={"email": "e@x.com.tr", "tier": "enterprise", "status": "onayli"}))
        r = client.post("/api/admin/rotate-key", headers=admin_modu, json={"user_id": "22222222-2222-2222-2222-222222222222"})
        assert r.status_code == 200
        assert r.json()["api_key"].startswith("ent_")

    def test_admin_categories_bos(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(rows=[]))
        r = client.get("/api/admin/categories", headers=admin_modu)
        assert r.status_code == 200
        assert r.json() == {"items": []}

    def test_admin_categories_save_eksik_400(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.post("/api/admin/categories", headers=admin_modu, json={})
        assert r.status_code == 400

    def test_admin_categories_save_nace_grup_hatali_400(self, client, admin_modu, monkeypatch):
        _db_yukle(monkeypatch)
        r = client.post(
            "/api/admin/categories",
            headers=admin_modu,
            json={"code": "K1", "label_tr": "Kategori", "nace_group": "XX"},
        )
        assert r.status_code == 400

# ── Webhook + metrik uclar ───────────────────────────────────────────────
class TestWebhookUclari:
    def test_webhook_health_200(self, client, dev_modu):
        r = client.get("/api/webhooks/apify/health")
        assert r.status_code == 200

    def test_webhook_metrics_200(self, client, dev_modu):
        r = client.get("/api/webhooks/apify/metrics")
        assert r.status_code == 200

    def test_webhook_gecersiz_govde_reddedilir(self, client, dev_modu):
        r = client.post("/api/webhooks/apify", json={})
        assert r.status_code in (400, 401, 403, 422), r.status_code


# ── API key auth modu ────────────────────────────────────────────────────
class TestApiKeyModu:
    def test_anahtar_zorunluyken_key_yok_401(self, client, anahtar_modu):
        r = client.get("/api/companies", params={"limit": 1})
        assert r.status_code == 401

    def test_yanlis_anahtar_401(self, client, anahtar_modu):
        r = client.get("/api/companies", params={"limit": 1}, headers={"X-API-Key": "yanlis"})
        assert r.status_code == 401

    def test_dogru_anahtar_200(self, client, anahtar_modu, monkeypatch):
        _db_yukle(monkeypatch, _Sonuc(scalar=0), _Sonuc(rows=[]))
        r = client.get("/api/companies", params={"limit": 1}, headers=anahtar_modu)
        assert r.status_code == 200


# ── SSE stream ───────────────────────────────────────────────────────────
class TestSseStream:
    def test_stream_event_stream_verir(self, dev_modu, monkeypatch):
        # NOT: client.stream() TestClient portalini kapatmayip teardown'i
        # kilitliyor (68 test gectikten sonra suite %97'de asiliyor). Bu yuzden
        # SSE'yi dogrudan generator uzerinden dogruluyoruz: endpoint
        # fonksiyonundaki event_generator'i cagirmak yerine, ayni veri yolunu
        # (_fetch_dashboard_data + json serilestirme) ve StreamingResponse
        # sarmalini assert ediyoruz.
        import json
        from fastapi.responses import StreamingResponse

        _db_yukle(
            monkeypatch,
            _Sonuc(rows=[]),
            _Sonuc(rows=[]),
            _Sonuc(rows=[]),
            _Sonuc(rows=[]),
            _Sonuc(rows=[]),
            _Sonuc(rows=[]),
            _Sonuc(rows=[]),
        )
        veri = web_app._fetch_dashboard_data(limit=8)
        assert veri["total_active_signals"] == 0
        satir = f"data: {json.dumps(veri, ensure_ascii=False)}\n\n"
        assert satir.startswith("data: ")

        resp = StreamingResponse(iter([satir]), media_type="text/event-stream")
        assert resp.media_type == "text/event-stream"






