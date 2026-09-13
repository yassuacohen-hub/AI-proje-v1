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
    monkeypatch.setattr(admin_auth, "post_api", lambda *args, **kwargs: {})

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
    monkeypatch.setattr(admin_auth, "post_api", lambda *args, **kwargs: (_ for _ in ()).throw(APIError("invalid credentials")))

    admin_auth.render_admin_login()

    assert "admin_token" not in state
    error.assert_called_once_with("Giriş başarısız: invalid credentials")
