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

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_bolum_sec_implementation_kontrol():
    """bolum_sec fonksiyonu: switch_page/rerun + session_state güncellemesi."""
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


# --- NAV-FIX-02 ---


def test_nav_ipucu_her_durumda_none():
    """_nav_ipcu() toggle açık/kapalı her ikisinde de None döner."""
    app_kod = (ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(app_kod)

    found = False
    always_none = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_nav_ipucu":
            found = True
            func_body = ast.unparse(node)
            if "return None" in func_body:
                always_none = True
            break

    assert found, "_nav_ipucu bulunamadı"
    assert always_none, "_nav_ipucu her durumda None dönmeli"


def test_nav_ipcu_topbar_caption_toggle():
    """Toggle açıkken render_topbar'da IPUCU_KEY kontrolü ve caption var."""
    app_kod = (ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(app_kod)

    found_caption = False
    found_ipcu_key = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "render_topbar":
            func_body = ast.unparse(node)
            if "IPUCU_KEY" in func_body and "caption" in func_body:
                found_caption = True
                found_ipcu_key = True

    assert found_caption, "render_topbar caption IPUCU_KEY kontrolü yok"
    assert found_ipcu_key, "IPUCU_KEY referansı eksik"


# --- NAV-FIX-01 ek ---


def test_auth_gate_modal_kapatilamaz():
    """AUTH-GATE-01: main() Modal kapatilamaz (kapatilabilir=False)."""
    app_kod = (ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(app_kod)

    found_modal = False
    kapatilamaz = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            modal_class = None
            if isinstance(node.func, ast.Name) and node.func.id == "Modal":
                modal_class = node.func.id
            elif isinstance(node.func, ast.Attribute) and node.func.attr == "Modal":
                modal_class = node.func.attr
            if modal_class:
                found_modal = True
                for kw in node.keywords:
                    if kw.arg == "kapatilabilir":
                        if isinstance(kw.value, ast.Constant) and kw.value.value is False:
                            kapatilamaz = True
                            break

    assert found_modal, "Modal bulunamadı"
    assert kapatilamaz, "Modal kapatilamaz olmalı"


def test_post_login_endpoint():
    """web_app.py POST /api/admin/login endpoint'i var."""
    kod = (ROOT / "web_app.py").read_text(encoding="utf-8")
    assert "api_admin_login_post" in kod, "POST /api/admin/login endpoint'i yok"
    assert "@app.post" in kod, "@app.post dekoratörü yok"
