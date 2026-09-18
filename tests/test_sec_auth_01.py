# -*- coding: utf-8 -*-
"""SEC-AUTH-01 Aşama B testleri (Y-1, Y-2, D-4, O-2, Y-4).

Kapsam:
- Y-1: auth uçlarında IP bazlı katı rate limit (5/dk → 429), genel kovadan bağımsız
- Y-2: login var/yok sızması yok (bilinmeyen e-posta ≡ hatalı şifre, tek 401 detayı);
  reset-request her durumda tek tip {ok: true}; UI st.error genel mesaj
- D-4: change-password şifre alanlarında .strip() yok
- O-2: admin_login_probe POST kullanır (GET + "405 beklenir" kalktı)
- Y-4: aktif_rol() "guest" (misafir) token'ı admin'e yükseltmez

Çalıştırma: pytest tests/test_sec_auth_01.py -q
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import web_app  # noqa: E402
from web_app import app  # noqa: E402

GENEL_HATA = "Giriş başarısız: e-posta/şifre kontrol ediniz."


# ── Sahte DB altyapısı (test_api_integration ile aynı desen) ─────────────
class _Sonuc:
    def __init__(self, first=None):
        self._first = first

    def first(self):
        return self._first

    def mappings(self):
        return self

    def all(self):
        return []

    def scalar(self):
        return None


class _FakeConn:
    def __init__(self, kuyruk):
        self._kuyruk = kuyruk

    def execute(self, stmt, *args, **kwargs):
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
    """web_app.get_engine'i sıralı sahte sonuçlarla değiştirir."""
    engine = _FakeEngine(list(sonuclar))
    monkeypatch.setattr(web_app, "get_engine", lambda: engine)
    return engine


@pytest.fixture()
def client(monkeypatch):
    """DB'siz açık (public) mod + temiz rate-limit kovaları."""
    monkeypatch.setattr(web_app, "DASH_API_KEY", "")
    monkeypatch.delenv("DASH_API_KEY", raising=False)
    web_app._RATE_LIMIT.clear()
    web_app._AUTH_RATE_LIMIT.clear()
    with TestClient(app) as c:
        yield c
    web_app._RATE_LIMIT.clear()
    web_app._AUTH_RATE_LIMIT.clear()


# ── Y-1: auth uçlarında katı rate limit ──────────────────────────────────
class TestY1AuthRateLimit:
    def test_admin_login_6_istekte_429(self, client, monkeypatch):
        """Limit 5/dk: 5 istek 401, 6. istek 429."""
        _db_yukle(monkeypatch, _Sonuc(first=None))
        for _ in range(5):
            r = client.post("/api/admin/login", json={"email": "a@b.c", "password": "x"})
            assert r.status_code == 401, r.text
        r = client.post("/api/admin/login", json={"email": "a@b.c", "password": "x"})
        assert r.status_code == 429
        assert "Cok fazla" in r.json()["detail"]

    def test_reset_request_5_sonra_429(self, client, monkeypatch):
        """reset-request de aynı guard'a bağlı (brute-force yavaşlatma)."""
        _db_yukle(monkeypatch, _Sonuc())
        for _ in range(5):
            r = client.post("/api/admin/reset-request", json={"email": "a@b.c"})
            assert r.status_code == 200, r.text
        r = client.post("/api/admin/reset-request", json={"email": "a@b.c"})
        assert r.status_code == 429

    def test_genel_kovadan_bagimsiz(self, client, monkeypatch):
        """_auth_rate_guard ayrı kova tutar: genel trafik auth limitini tüketmez."""
        _db_yukle(monkeypatch, _Sonuc(first=None))
        assert client.get("/api/health").status_code == 200
        r = client.post("/api/admin/login", json={"email": "a@b.c", "password": "x"})
        assert r.status_code == 401

    def test_dort_auth_ucu_guard_bagli(self):
        """Login + reset-request + reset-confirm + change-password → 4 Depends."""
        kod = (ROOT / "web_app.py").read_text(encoding="utf-8")
        assert kod.count("Depends(_auth_rate_guard)") >= 4


# ── Y-2: var/yok sızması yok ─────────────────────────────────────────────
class TestY2VarYokSizmasi:
    def test_login_bilinmeyen_email_ve_yanlis_sifre_ayni_401(self, client, monkeypatch):
        """Bilinmeyen e-posta ≡ hatalı şifre: aynı 401 + aynı detay."""
        from web_app import _hash_password

        _db_yukle(
            monkeypatch,
            _Sonuc(first=None),
            _Sonuc(first={
                "email": "k@f.com",
                "password_hash": _hash_password("dogru-sifre"),
                "role": "admin",
                "status": "onayli",
            }),
        )
        r1 = client.post("/api/admin/login", json={"email": "yok@f.com", "password": "x"})
        r2 = client.post("/api/admin/login", json={"email": "k@f.com", "password": "yanlis"})
        assert r1.status_code == 401 and r2.status_code == 401
        assert r1.json()["detail"] == r2.json()["detail"]
        assert r1.json()["detail"] == "gecersiz email veya sifre"

    def test_reset_request_bilinmeyen_email_tek_tip_ok(self, client, monkeypatch):
        """Bilinmeyen e-postada da {ok: true} — 404 'admin bulunamadi' yok."""
        _db_yukle(monkeypatch, _Sonuc())
        r = client.post("/api/admin/reset-request", json={"email": "yok@f.com"})
        assert r.status_code == 200
        assert r.json() == {"ok": True, "message": "sifirlama linki gonderildi"}

    def test_ui_apierror_genel_mesaj_gosterir(self, monkeypatch):
        """Y-2 UI: APIError detayı ekrana sızmaz; genel mesaj gösterilir."""
        from scripts.dash04_api_client import APIError
        from web_dashboard.tabs import admin_auth

        state: dict = {}
        monkeypatch.setattr(admin_auth.st, "session_state", state)
        monkeypatch.setattr(admin_auth.st, "form", lambda *a, **k: MagicMock())
        monkeypatch.setattr(admin_auth.st, "text_input", lambda *a, **k: "a@b.c")
        monkeypatch.setattr(admin_auth.st, "form_submit_button", lambda *a, **k: True)
        error = MagicMock()
        monkeypatch.setattr(admin_auth.st, "error", error)
        # Bu test yalnız giriş formunu ölçer: `render_admin_login()` sonunda
        # çağrılan reset akışı, global `form_submit_button=True` yüzünden
        # gönderilmiş sayılıp ek st.error üretiyor. Gerçek Streamlit'te her
        # formun submit'i ayrıdır.
        monkeypatch.setattr(admin_auth, "render_sifre_unuttum", MagicMock())
        monkeypatch.setattr(
            admin_auth,
            "post_api",
            lambda *a, **k: (_ for _ in ()).throw(APIError("HTTP 401: gecersiz sifre DETAY")),
        )

        admin_auth.render_admin_login()

        error.assert_called_once_with(GENEL_HATA)
        # Sunucu detayı ekrana sızmamalı:
        assert not any("DETAY" in str(c) for c in error.call_args_list)


# ── D-4: change-password .strip() kaldırma ───────────────────────────────
class TestD4Strip:
    def test_change_password_sifre_alanlarinda_strip_yok(self):
        kod = (ROOT / "web_app.py").read_text(encoding="utf-8")
        agac = ast.parse(kod)
        for node in ast.walk(agac):
            if isinstance(node, ast.FunctionDef) and node.name == "api_admin_change_password":
                govde = ast.unparse(node)
                satirlar = [
                    s for s in govde.splitlines()
                    if "old_password" in s or "new_password" in s
                ]
                assert satirlar, "şifre alanları bulunamadı"
                kirli = [s for s in satirlar if ".strip()" in s]
                assert not kirli, f"D-4: şifre alanında .strip() kaldı: {kirli}"
                return
        pytest.fail("api_admin_change_password bulunamadı")


# ── O-2: probe POST kullanır ─────────────────────────────────────────────
class TestO2Probe:
    def test_probe_post_kullanir_get_ve_405_kalkti(self):
        kod = (ROOT / "scripts" / "admin_login_probe.py").read_text(encoding="utf-8")
        assert "requests.post(" in kod, "probe POST kullanmalı (O-2)"
        assert "requests.get(" not in kod, "probe'da GET kalmış"
        assert "405" not in kod, "'405 beklenir' notu kalkmalı"


# ── Y-4: misafir token'i admin'e yükseltmez ──────────────────────────────
class TestY4AktifRol:
    def test_aktif_rol_guest_anona_indirgenir(self):
        kod = (ROOT / "app.py").read_text(encoding="utf-8")
        agac = ast.parse(kod)
        for node in ast.walk(agac):
            if isinstance(node, ast.FunctionDef) and node.name == "aktif_rol":
                govde = ast.unparse(node)
                assert '"guest"' in govde, 'aktif_rol "guest" token ini ayırt etmeli'
                assert "ROL_ANON" in govde, "misafir ROL_ANON a indirgenmeli"
                return
        pytest.fail("aktif_rol bulunamadı")
