# -*- coding: utf-8 -*-
"""MVP-KUL-01 testleri: render_user_management."""
from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest

from scripts.dash04_api_client import APIError
from web_dashboard.tabs.admin_extras import render_user_management


def test_render_user_management_uses_pageheader_fixed(monkeypatch):
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

    monkeypatch.setattr("company_master.ui.PageHeader", FakePageHeader)
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st", st_mock)
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.get_api", lambda *a, **kw: {})
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.post_api", MagicMock())

    render_user_management(token="tok")
    assert captured.get("baslik") == "Kullan\u0131c\u0131 Y\u00f6netimi"
    assert captured.get("giris") == "Onay bekleyen kullan\u0131c\u0131lar\u0131 y\u00f6netin ve kredi paketi tan\u0131mlay\u0131n."
    assert captured.get("ust_etiket") == "?? ? Y?netim"
    assert captured.get("ikon") == "??"
    assert captured.get("rendered") is True
