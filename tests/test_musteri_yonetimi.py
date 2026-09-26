# -*- coding: utf-8 -*-
"""NAV-IA-02: Müşteri Yönetimi testleri.

Kapsam:
- 6 alt sekme mevcut
- K-1: Tier secimleri modul seviyesinde taniliyor (sabit liste disindan cikarilmali)
- render_musteri_yonetimi_tab cagirilabilir
- D-215: render_paket_kredi_tab (Gelir Kapısı kanonik kredi formu)
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from scripts.dash04_api_client import APIError
import web_dashboard.tabs.admin_extras as admin_extras_mod
from web_dashboard.tabs import musteri_yonetimi


# --------------------------------------------------------------------------- #
# K-1: Tier secimleri JSON konfigurasyonda
# --------------------------------------------------------------------------- #


def test_tier_secimler_json_konfigurasyon():
    """K-1: TIER_SECIMLERI modül seviyesinde tanýmlý."""
    assert hasattr(admin_extras_mod, "TIER_SECIMLERI")
    assert isinstance(admin_extras_mod.TIER_SECIMLERI, list)
    assert set(admin_extras_mod.TIER_SECIMLERI) == {"terminal", "strategic", "enterprise"}


# --------------------------------------------------------------------------- #
# Müşteri Yönetimi sayfa
# --------------------------------------------------------------------------- #


def test_musteri_yonetimi_render_fonksiyonu_mevcut():
    """render_musteri_yonetimi_tab cagirilabilir."""
    assert callable(musteri_yonetimi.render_musteri_yonetimi_tab)


def test_musteri_yonetimi_6_alt_sekme():
    """7 alt sekme mevcut (st.tabs ile) — D-214: Upsell Adayları eklendi."""
    st_mock = MagicMock()
    st_mock.tabs = MagicMock(return_value=[MagicMock() for _ in range(7)])
    st_mock.subheader = MagicMock()
    st_mock.divider = MagicMock()
    st_mock.info = MagicMock()
    st_mock.caption = MagicMock()
    st_mock.columns = lambda n: [MagicMock() for _ in range(n)]
    st_mock.form = MagicMock(return_value=MagicMock())
    st_mock.text_input = MagicMock(return_value="")
    st_mock.number_input = MagicMock(return_value=50)
    st_mock.form_submit_button = MagicMock(return_value=False)
    st_mock.selectbox = MagicMock(return_value="terminal")

    ph_mock = MagicMock()
    ph_mock.render = MagicMock()

    admin_destek = MagicMock()
    admin_destek.render_destek_tab = MagicMock()

    admin_export = MagicMock()
    admin_export.render_export_tab = MagicMock()

    with patch.object(musteri_yonetimi, "st", st_mock), patch.object(
        musteri_yonetimi, "PageHeader", lambda *a, **kw: ph_mock
    ), patch.object(
        musteri_yonetimi, "admin_destek", admin_destek
    ), patch.object(
        musteri_yonetimi, "admin_export", admin_export
    ), patch(
        "web_dashboard.tabs.admin_extras.post_api", MagicMock()
    ), patch(
        "web_dashboard.tabs.admin_extras.get_api", MagicMock(return_value={"items": []})
    ):
        with patch(
            "web_dashboard.tabs.musteri_yonetimi.render_user_management", MagicMock()
        ):
            musteri_yonetimi.render_musteri_yonetimi_tab()

    assert ph_mock.render.called
    assert admin_destek.render_destek_tab.called
    assert admin_export.render_export_tab.called
    assert st_mock.tabs.called
    sekme_sayisi = len(st_mock.tabs.call_args[0][0])
    assert sekme_sayisi == 7


# --------------------------------------------------------------------------- #
# D-215: render_paket_kredi_tab — Gelir Kapısı kanonik kredi formu
# --------------------------------------------------------------------------- #


def test_render_paket_kredi_tab_credit_form(monkeypatch):
    st_mock = MagicMock()
    st_mock.session_state = {"admin_token": "tok"}
    st_mock.cache_data = MagicMock()
    st_mock.cache_data.clear = MagicMock()

    form_submit_calls = []

    class FakeForm:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    st_mock.form = FakeForm
    st_mock.text_input = lambda label, value="", placeholder="": "uid123" if label == "Kullanıcı ID" else ""
    st_mock.number_input = lambda label, min_value=None, value=None: 75
    st_mock.columns = lambda n: [MagicMock() for _ in range(n)]

    def track_form_submit(label, type=None):
        form_submit_calls.append(label)
        return True
    st_mock.form_submit_button = track_form_submit

    post_calls = []

    def fake_post_api(endpoint, json=None, token=None):
        post_calls.append({"endpoint": endpoint, "json": json, "token": token})
        return {"ok": True}

    monkeypatch.setattr(musteri_yonetimi, "st", st_mock)
    monkeypatch.setattr(musteri_yonetimi, "PageHeader", MagicMock())
    monkeypatch.setattr(musteri_yonetimi, "post_api", fake_post_api)
    monkeypatch.setattr(musteri_yonetimi, "get_api", lambda endpoint, token=None: {"items": []})

    musteri_yonetimi.render_paket_kredi_tab()
    assert "Kredi Yükle" in form_submit_calls
    assert any(c["endpoint"] == "/api/admin/credit" for c in post_calls)
    credit_call = [c for c in post_calls if c["endpoint"] == "/api/admin/credit"][0]
    assert credit_call["json"] == {"user_id": "uid123", "amount": 75}


def test_render_paket_kredi_tab_credit_error(monkeypatch):
    st_mock = MagicMock()
    st_mock.session_state = {"admin_token": "tok"}
    st_mock.cache_data = MagicMock()
    st_mock.cache_data.clear = MagicMock()

    class FakeForm:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    st_mock.form = FakeForm
    st_mock.text_input = lambda label, value="", placeholder="": "uid_err"
    st_mock.number_input = lambda label, min_value=None, value=None: 10
    st_mock.columns = lambda n: [MagicMock() for _ in range(n)]
    st_mock.form_submit_button = lambda label, type=None: True

    def fake_post_api(endpoint, json=None, token=None):
        if endpoint == "/api/admin/credit":
            raise APIError("bakiye yetersiz")
        return {}

    monkeypatch.setattr(musteri_yonetimi, "st", st_mock)
    monkeypatch.setattr(musteri_yonetimi, "PageHeader", MagicMock())
    monkeypatch.setattr(musteri_yonetimi, "post_api", fake_post_api)
    monkeypatch.setattr(musteri_yonetimi, "get_api", lambda endpoint, token=None: {"items": []})

    musteri_yonetimi.render_paket_kredi_tab()
    st_mock.error.assert_called()
    err_msg = str(st_mock.error.call_args[0][0])
    assert "Kredi yükleme başarısız" in err_msg
