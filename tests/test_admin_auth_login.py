from unittest.mock import MagicMock

import pytest

from scripts.dash04_api_client import APIError
from web_dashboard.tabs import admin_auth


@pytest.fixture(autouse=True)
def _reset_akisi_yalit(monkeypatch):
    """Giriş testleri yalnız giriş formunu ölçer.

    `render_admin_login()` sonunda `render_sifre_unuttum()` çağrılıyor; bu
    testler `form_submit_button`'ı global `True` yaptığı için reset formu da
    gönderilmiş sayılıyordu. Gerçek Streamlit'te her formun submit'i ayrıdır.
    """
    monkeypatch.setattr(admin_auth, "render_sifre_unuttum", MagicMock())


def _form_hazirla(monkeypatch, state: dict) -> None:
    """Form + text_input + submit sahteleri (giriş formu tıklanmış gibi)."""
    monkeypatch.setattr(admin_auth.st, "session_state", state)
    monkeypatch.setattr(admin_auth.st, "form", lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr(admin_auth.st, "text_input", lambda *args, **kwargs: "admin@huginn.local")
    monkeypatch.setattr(admin_auth.st, "form_submit_button", lambda *args, **kwargs: True)
    monkeypatch.setattr(admin_auth.st, "caption", MagicMock())
    monkeypatch.setattr(admin_auth.st, "subheader", MagicMock())


def test_render_admin_login_clears_stale_token_and_shows_clear_error(monkeypatch):
    state: dict = {}
    monkeypatch.setattr(admin_auth.st, "session_state", state)
    monkeypatch.setattr(admin_auth.st, "form", lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr(admin_auth.st, "text_input", lambda *args, **kwargs: "admin@huginn.local")
    monkeypatch.setattr(admin_auth.st, "form_submit_button", lambda *args, **kwargs: True)
    error = MagicMock()
    monkeypatch.setattr(admin_auth.st, "error", error)
    monkeypatch.setattr(admin_auth, "post_api", lambda *args, **kwargs: {})

    admin_auth.render_admin_login()

    assert "admin_token" not in state
    error.assert_called_once_with("Giriş başarısız: e-posta/şifre kontrol ediniz.")


def test_render_admin_login_clears_token_on_api_error(monkeypatch):
    state: dict = {}
    monkeypatch.setattr(admin_auth.st, "session_state", state)
    monkeypatch.setattr(admin_auth.st, "form", lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr(admin_auth.st, "text_input", lambda *args, **kwargs: "admin@huginn.local")
    monkeypatch.setattr(admin_auth.st, "form_submit_button", lambda *args, **kwargs: True)
    error = MagicMock()
    monkeypatch.setattr(admin_auth.st, "error", error)
    monkeypatch.setattr(admin_auth, "post_api", lambda *args, **kwargs: (_ for _ in ()).throw(APIError("invalid credentials")))

    admin_auth.render_admin_login()

    assert "admin_token" not in state
    # SEC-AUTH-01 Y-2: sunucu detayı genel mesajla gizlenir.
    error.assert_called_once_with("Giriş başarısız: e-posta/şifre kontrol ediniz.")


def test_render_admin_login_uses_post_with_json(monkeypatch):
    """AUTH-GATE-01: web_app `/api/admin/login` POST + JSON body bekler."""
    state: dict = {}
    monkeypatch.setattr(admin_auth.st, "session_state", state)
    monkeypatch.setattr(admin_auth.st, "form", lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr(admin_auth.st, "text_input", lambda *args, **kwargs: "admin@huginn.local")
    monkeypatch.setattr(admin_auth.st, "form_submit_button", lambda *args, **kwargs: True)
    monkeypatch.setattr(admin_auth.st, "success", MagicMock())
    monkeypatch.setattr(admin_auth.st, "rerun", MagicMock())
    cagri: dict = {}

    def sahte_post(endpoint, json=None, **kwargs):
        cagri["endpoint"] = endpoint
        cagri["json"] = json
        return {"token": "tok-1"}

    monkeypatch.setattr(admin_auth, "post_api", sahte_post)

    admin_auth.render_admin_login()

    assert cagri["endpoint"] == "/api/admin/login"
    assert cagri["json"] == {"email": "admin@huginn.local", "password": "admin@huginn.local"}
    assert state["admin_token"] == "tok-1"


def test_render_admin_login_token_varken_form_yerine_oturum_gosterir(monkeypatch):
    """D-24: token varken form çizilmez; flash + çıkış + görünür bölüm bilgisi gösterilir."""
    state = {"admin_token": "tok-1", "admin_email": "a@b.c", admin_auth._FLASH_KEY: {"mesaj": "ok", "tur": "success"}}
    _form_hazirla(monkeypatch, state)
    success, info, cikis = MagicMock(), MagicMock(), MagicMock()
    monkeypatch.setattr(admin_auth.st, "success", success)
    monkeypatch.setattr(admin_auth.st, "info", info)
    monkeypatch.setattr(admin_auth, "render_admin_cikis", cikis)
    monkeypatch.setattr(admin_auth, "post_api", lambda *a, **k: pytest.fail("token varken API çağrılmamalı"))

    admin_auth.render_admin_login()

    success.assert_called_once_with("ok")
    cikis.assert_called_once()
    assert admin_auth._FLASH_KEY not in state
    assert "bölüm görünür" in info.call_args[0][0]


def test_render_admin_login_401_ipucu_verir(monkeypatch):
    """D-24: 401 → .env/DB şifre uyumsuzluğu ipucu (admin_env_eslesme + admin_sifre_sifirla)."""
    state: dict = {}
    _form_hazirla(monkeypatch, state)
    caption = MagicMock()
    monkeypatch.setattr(admin_auth.st, "caption", caption)
    monkeypatch.setattr(admin_auth.st, "error", MagicMock())
    monkeypatch.setattr(
        admin_auth, "post_api", lambda *a, **k: (_ for _ in ()).throw(APIError("API HTTP 401 hatası: gecersiz sifre"))
    )

    admin_auth.render_admin_login()

    assert any("admin_env_eslesme" in str(c.args[0]) for c in caption.call_args_list)
