from unittest.mock import MagicMock

import pytest

from scripts.dash04_api_client import APIError
from web_dashboard.tabs import admin_auth


def test_render_admin_login_clears_stale_token_and_shows_clear_error(monkeypatch):
    state = {"admin_token": "stale-token"}
    monkeypatch.setattr(admin_auth.st, "session_state", state)
    monkeypatch.setattr(admin_auth.st, "form", lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr(admin_auth.st, "text_input", lambda *args, **kwargs: "admin@huginn.local")
    monkeypatch.setattr(admin_auth.st, "form_submit_button", lambda *args, **kwargs: True)
    error = MagicMock()
    monkeypatch.setattr(admin_auth.st, "error", error)
    monkeypatch.setattr(admin_auth, "get_api", lambda *args, **kwargs: {})

    admin_auth.render_admin_login()

    assert "admin_token" not in state
    error.assert_called_once_with("Giriş başarısız: e-posta/şifre kontrol ediniz.")


def test_render_admin_login_clears_token_on_api_error(monkeypatch):
    state = {"admin_token": "stale-token"}
    monkeypatch.setattr(admin_auth.st, "session_state", state)
    monkeypatch.setattr(admin_auth.st, "form", lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr(admin_auth.st, "text_input", lambda *args, **kwargs: "admin@huginn.local")
    monkeypatch.setattr(admin_auth.st, "form_submit_button", lambda *args, **kwargs: True)
    error = MagicMock()
    monkeypatch.setattr(admin_auth.st, "error", error)
    monkeypatch.setattr(admin_auth, "get_api", lambda *args, **kwargs: (_ for _ in ()).throw(APIError("invalid credentials")))

    admin_auth.render_admin_login()

    assert "admin_token" not in state
    error.assert_called_once_with("Giriş başarısız: invalid credentials")


def test_render_admin_login_uses_get_with_query_params(monkeypatch):
    """MVP-KUL-FIX-01: web_app `/api/admin/login` GET+query bekler; POST 405 doner."""
    state: dict = {}
    monkeypatch.setattr(admin_auth.st, "session_state", state)
    monkeypatch.setattr(admin_auth.st, "form", lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr(admin_auth.st, "text_input", lambda *args, **kwargs: "admin@huginn.local")
    monkeypatch.setattr(admin_auth.st, "form_submit_button", lambda *args, **kwargs: True)
    monkeypatch.setattr(admin_auth.st, "success", MagicMock())
    monkeypatch.setattr(admin_auth.st, "rerun", MagicMock())
    cagri: dict = {}

    def sahte_get(endpoint, params=None, **kwargs):
        cagri["endpoint"] = endpoint
        cagri["params"] = params
        return {"token": "tok-1"}

    monkeypatch.setattr(admin_auth, "get_api", sahte_get)

    admin_auth.render_admin_login()

    assert cagri["endpoint"] == "/api/admin/login"
    assert cagri["params"] == {"email": "admin@huginn.local", "password": "admin@huginn.local"}
    assert state["admin_token"] == "tok-1"
