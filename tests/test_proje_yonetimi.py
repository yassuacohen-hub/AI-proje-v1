# -*- coding: utf-8 -*-
"""NAV-IA-03: Proje Yönetimi testleri.

Kapsam:
- 5 alt sekme mevcut (Karar Defteri üstte)
- PageHeader + Section (ADMIN-UI-10) deseni
- st.subheader yok
- Mevcut render fonksiyonları çağrılıyor
"""
from __future__ import annotations

from unittest.mock import MagicMock

import web_dashboard.tabs.proje_yonetimi as proje
from web_dashboard.tabs import admin_panel, abrakadabra, admin_audit, admin_errors, admin_dlq


def test_proje_yonetimi_render_fonksiyonu_mevcut():
    """render_proje_yonetimi_tab cagirilabilir."""
    assert callable(proje.render_proje_yonetimi_tab)


def test_proje_yonetimi_5_alt_sekme():
    """5 alt sekme mevcut, Karar Defteri en üstte."""
    basliklar = [b.baslik for b in proje.BOLUMLER]
    assert len(basliklar) == 5
    assert basliklar[0] == "Karar Defteri"
    assert "9Router" in basliklar[1] or "Abrakadabra" in basliklar[1]
    assert "Denetim" in basliklar[2]
    assert "Hata" in basliklar[3]
    assert "DLQ" in basliklar[4]


def test_proje_yonetimi_admin_ui_10():
    """PageHeader ve Section kullaniliyor, subheader yok."""
    import ast

    agac = ast.parse(open("web_dashboard/tabs/proje_yonetimi.py", encoding="utf-8").read())

    isimler = set()
    for node in ast.walk(agac):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            isimler.add(node.value.id + "." + node.attr)
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                isimler.add(node.func.id)
        if isinstance(node, ast.Attribute):
            isimler.add(node.attr)

    assert "PageHeader" in isimler, "PageHeader kullanilmali"
    assert "Section" in isimler, "Section kullanilmali"

    subheader_cagrilar = []
    for node in ast.walk(agac):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "subheader"
        ):
            subheader_cagrilar.append(node)
    assert not subheader_cagrilar, f"st.subheader kullanimi var: {len(subheader_cagrilar)}"


def test_render_tum_fonksiyonlar_cagiriliyor(monkeypatch):
    """Alt sekme fonksiyonlari cagiriliyor."""
    st_mock = MagicMock()
    st_mock.tabs = MagicMock(return_value=[MagicMock() for _ in range(5)])

    monkeypatch.setattr(proje, "st", st_mock)

    ph_mock = MagicMock()
    ph_mock.render = MagicMock()
    monkeypatch.setattr(proje, "PageHeader", lambda *a, **kw: ph_mock)

    secim = [MagicMock() for _ in range(5)]
    st_mock.tabs.return_value = secim

    section_mock = MagicMock()
    monkeypatch.setattr(proje, "Section", lambda *a, **kw: section_mock)

    # Mock the render functions
    for mod in [admin_panel, abrakadabra, admin_audit, admin_errors, admin_dlq]:
        for fn_name in dir(mod):
            if fn_name.startswith("render_"):
                fn = getattr(mod, fn_name)
                if callable(fn):
                    monkeypatch.setattr(mod, fn_name, MagicMock())

    monkeypatch.setattr(proje.admin_panel, "render_decision_tab", MagicMock())
    monkeypatch.setattr(proje.abrakadabra, "render_abrakadabra_tab", MagicMock())
    monkeypatch.setattr(proje.admin_audit, "render_audit_tab", MagicMock())
    monkeypatch.setattr(proje.admin_errors, "render_errors_tab", MagicMock())
    monkeypatch.setattr(proje.admin_dlq, "render_dlq_tab", MagicMock())

    proje.render_proje_yonetimi_tab()

    assert ph_mock.render.called
    admin_panel.render_decision_tab.assert_called_once()
    abrakadabra.render_abrakadabra_tab.assert_called_once()
    admin_audit.render_audit_tab.assert_called_once()
    admin_errors.render_errors_tab.assert_called_once()
    admin_dlq.render_dlq_tab.assert_called_once()
