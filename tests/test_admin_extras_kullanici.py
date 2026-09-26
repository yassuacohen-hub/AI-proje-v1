# -*- coding: utf-8 -*-
"""MVP-KUL-01 testleri: render_user_management."""
from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest

from scripts.dash04_api_client import APIError
from web_dashboard.tabs.admin_extras import render_user_management


def test_render_user_management_uses_pageheader(monkeypatch):
    captured = {}

    class FakePageHeader:
        def __init__(self, baslik="", giris="", *, ust_etiket="", ikon="", aksiyonlar=(), kimlig="", **kw):
            captured["baslik"] = baslik
            captured["giris"] = giris
            captured["ust_etiket"] = ust_etiket
            captured["ikon"] = ikon

        def render(self):
            captured["rendered"] = True

    st_mock = MagicMock()
    st_mock.session_state = {"admin_token": "tok"}
    st_mock.cache_data = MagicMock()
    st_mock.cache_data.clear = MagicMock()
    form_ctx = MagicMock()
    form_ctx.form_submit_button = MagicMock(return_value=False)
    form_ctx.__enter__ = MagicMock(return_value=form_ctx)
    form_ctx.__exit__ = MagicMock(return_value=False)
    st_mock.form = MagicMock(return_value=form_ctx)
    st_mock.columns = lambda sizes: [MagicMock(), MagicMock()]

    monkeypatch.setattr("web_dashboard.tabs.admin_extras.PageHeader", FakePageHeader)
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st", st_mock)
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.get_api", lambda *a, **kw: {})
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.post_api", MagicMock())

    render_user_management(token="tok")

    assert captured.get("baslik") == "Kullan\u0131c\u0131 Y\u00f6netimi"
    assert captured.get("giris") == "Onay bekleyen kullan\u0131c\u0131lar\u0131 y\u00f6netin ve kredi paketi tan\u0131mlay\u0131n."
    assert captured.get("ust_etiket") == "İş · Yönetim"
    assert captured.get("ikon") == "👥"
    assert captured.get("rendered") is True


def test_render_user_management_token_yok_warning(monkeypatch):
    st_mock = MagicMock()
    st_mock.session_state = {}
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st", st_mock)
    render_user_management(token=None)
    st_mock.warning.assert_called_with("L\u00fctfen giri\u015f yap\u0131n")


def test_render_user_management_approve_button(monkeypatch):
    import company_master.ui as ui_mod
    monkeypatch.setattr(ui_mod, "PageHeader", MagicMock())
    st_mock = MagicMock()
    st_mock.session_state = {"admin_token": "tok"}
    st_mock.cache_data = MagicMock()
    st_mock.cache_data.clear = MagicMock()

    button_pressed = []

    def fake_button(label, key=None):
        if key == "approve_u42":
            button_pressed.append(key)
            return True
        return False

    st_mock.button = fake_button
    st_mock.columns = lambda sizes: [MagicMock(), MagicMock()]
    form_ctx = MagicMock()
    form_ctx.form_submit_button = MagicMock(return_value=False)
    form_ctx.__enter__ = MagicMock(return_value=form_ctx)
    form_ctx.__exit__ = MagicMock(return_value=False)
    st_mock.form = MagicMock(return_value=form_ctx)
    st_mock.selectbox = lambda label, options, index, key=None, label_visibility="visible": options[index] if 0 <= index < len(options) else options[0]

    post_calls = []

    def fake_post_api(endpoint, json=None, token=None):
        post_calls.append({"endpoint": endpoint, "json": json, "token": token})
        return {"ok": True}

    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st", st_mock)
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.post_api", fake_post_api)
    monkeypatch.setattr(
        "web_dashboard.tabs.admin_extras.get_api",
        lambda endpoint, token=None: {
            "bekleyen": [{"user_id": "u42", "email": "a@b.com", "company_name": "X", "tier": "free"}],
            "onayli_son": [],
        }
        if endpoint == "/api/admin/pending"
        else {"items": []},
    )

    render_user_management(token="tok")
    assert "approve_u42" in button_pressed
    assert any(c["endpoint"] == "/api/admin/approve" for c in post_calls)
    approve_call = [c for c in post_calls if c["endpoint"] == "/api/admin/approve"][0]
    assert approve_call["json"] == {"user_id": "u42", "tier": "terminal"}
    assert approve_call["token"] == "tok"


def test_render_user_management_approve_error(monkeypatch):
    import company_master.ui as ui_mod
    monkeypatch.setattr(ui_mod, "PageHeader", MagicMock())
    st_mock = MagicMock()
    st_mock.session_state = {"admin_token": "tok"}
    st_mock.cache_data = MagicMock()
    st_mock.cache_data.clear = MagicMock()

    def fake_button(label, key=None):
        if key == "approve_u1":
            return True
        return False

    st_mock.button = fake_button
    st_mock.columns = lambda sizes: [MagicMock(), MagicMock()]
    form_ctx = MagicMock()
    form_ctx.form_submit_button = MagicMock(return_value=False)
    form_ctx.__enter__ = MagicMock(return_value=form_ctx)
    form_ctx.__exit__ = MagicMock(return_value=False)
    st_mock.form = MagicMock(return_value=form_ctx)

    def fake_post_api(endpoint, json=None, token=None):
        if endpoint == "/api/admin/approve":
            raise APIError("yetkisiz")
        return {}

    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st", st_mock)
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.post_api", fake_post_api)
    monkeypatch.setattr(
        "web_dashboard.tabs.admin_extras.get_api",
        lambda endpoint, token=None: {
            "bekleyen": [{"user_id": "u1", "email": "err@test.com", "company_name": "Y", "tier": "free"}],
            "onayli_son": [],
        }
        if endpoint == "/api/admin/pending"
        else {"items": []},
    )

    render_user_management(token="tok")
    st_mock.error.assert_called()
    err_msg = str(st_mock.error.call_args[0][0])
    assert "Onaylama ba\u015far\u0131s\u0131z" in err_msg


# D-215: Kredi formu admin_extras'tan kaldırıldı; kanonik yer
# musteri_yonetimi.render_paket_kredi_tab() → bkz. test_musteri_yonetimi.py
# test_render_paket_kredi_tab_credit_form / _credit_error.
