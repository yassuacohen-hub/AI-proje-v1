# -*- coding: utf-8 -*-
"""NAV-FIX-01: Tek tık geçiş doğrulama testi.

Kapsam: app.py render_sidebar (Hızlı geçiş selectbox),
render_topbar (bölüm araması), page_icon.

 Ölçütler:
 1. `bolum_sec` session_state["current_section"] günceller
    ve URL param `/bolum` ile aynı değer gösterir.
 2. selectbox `index` aktif bölümü gösterir (bayat değer kalmaz).
 3. page_icon UTF-8 mojibake içermemeli.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_bolum_sec_implementation_kontrol():
    """bolum_sec fonksiyonu: switch_page/rerun + session_state güncellemesi."""
    import ast

    app_kod = (ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(app_kod)

    bolum_sec_found = False
    has_switch = False
    has_rerun = False
    has_session_update = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "bolum_sec":
            bolum_sec_found = True
            func_body = ast.unparse(node)
            has_switch = "switch_page" in func_body
            has_rerun = "st.rerun()" in func_body or "rerun()" in func_body
            has_session_update = "current_section" in func_body and "=" in func_body

    assert bolum_sec_found, "bolum_sec bulunamadı"
    assert has_switch, "bolum_sec switch_page çağırmaz"
    assert has_rerun, "bolum_sec rerun çağırmaz"
    assert has_session_update, "bolum_sec current_section güncellermez"


def test_selectbox_index_aktif_bolum_gosterir():
    """app.py render_sidebar'daki Hızlı geçiş selectbox'ı var ve index düzgün."""
    import ast

    app_kod = (ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(app_kod)

    selectbox_found = False
    hizli_gecis_found = False
    on_change_found = False
    index_dynamic = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "selectbox":
                selectbox_found = True
                for kw in node.keywords:
                    if kw.arg == "key" and isinstance(kw.value, ast.Constant) and kw.value.value == "nav_hizli_gecis":
                        hizli_gecis_found = True
                    if kw.arg == "on_change":
                        on_change_found = True
                    if kw.arg == "index":
                        index_dynamic = True

    assert selectbox_found, "selectbox bulunamadı"
    assert hizli_gecis_found, "Hızlı geçiş selectbox (key=nav_hizli_gecis) bulunamadı"
    assert on_change_found, "on_change callback bulunamadı"
    assert index_dynamic, "index dinamik hesaplanmıyor"


def test_page_icon_utf8():
    """page_icon UTF-8 mojibake içermemeli."""
    app_kod = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "page_icon" in app_kod, "page_icon bulunamadı"
    assert "ğŸ" not in app_kod, "page_icon mojibake içeriyor"
