# -*- coding: utf-8 -*-
"""NAV-IA-02: Müşteri Yönetimi testleri.

Kapsam:
- 6 alt sekme mevcut
- K-1: Tier secimleri modul seviyesinde taniliyor (sabit liste disindan cikarilmali)
- render_musteri_yonetimi_tab cagirilabilir
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

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
    """6 alt sekme mevcut (st.tubs ile)."""
    st_mock = MagicMock()
    st_mock.tabs = MagicMock(return_value=[MagicMock() for _ in range(6)])
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
    assert sekme_sayisi == 6
