# -*- coding: utf-8 -*-
"""NAV-IA-04: Hesap kartı popover testleri.

Kapsam:
- _hesap_karti_popover() fonksiyonu app.py'de tanımlı
- render_sidebar() sonunda _hesap_karti_popover() çağrısı var
- Popover içinde "Şifre Değiştir" butonu (admin)
- Popover içinde "Çıkış" butonu (admin)
- Popover içinde "Giriş Yap" butonu (misafir)
- render_yonetim_bilesik app.py'de tanımlı DEĞİL
- _force_auth_gate session flag entegrasyonu
- eski_url_yonlendirme güncel
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_hesap_karti_popover_fonksiyon_mevcut():
    """NAV-IA-04: _hesap_karti_popover() app.py'de tanımlı."""
    kod = (ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    found = False
    has_popover = False
    has_token = False
    has_guest_btn = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_hesap_karti_popover":
            found = True
            func_body = ast.unparse(node)
            has_popover = "st.popover" in func_body
            has_token = "get_admin_token" in func_body
            has_guest_btn = "Giriş Yap" in func_body or "giris" in func_body.lower()
            break

    assert found, "_hesap_karti_popover bulunamadı"
    assert has_popover, "st.popover kullanılmıyor"
    assert has_token, "get_admin_token kullanılmıyor"
    assert has_guest_btn, "Giriş Yap butonu eksik"


def test_render_sidebar_popover_cagrisi():
    """NAV-IA-04: render_sidebar() _hesap_karti_popover() çağırır."""
    kod = (ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    sidebar_found = False
    calls_popover = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "render_sidebar":
            sidebar_found = True
            func_body = ast.unparse(node)
            calls_popover = "_hesap_karti_popover()" in func_body
            break

    assert sidebar_found, "render_sidebar bulunamadı"
    assert calls_popover, "render_sidebar _hesap_karti_popover() çağırmaz"


def test_popover_admin_butonlari():
    """NAV-IA-04: Popover içinde admin butonları (Şifre Değiştir, Çıkış)."""
    kod = (ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    func_body = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_hesap_karti_popover":
            func_body = ast.unparse(node)
            break

    assert func_body is not None, "_hesap_karti_popover bulunamadı"
    assert "Şifre Değiştir" in func_body, "Şifre Değiştir butonu eksik"
    assert "Çıkış" in func_body, "Çıkış butonu eksik"


def test_render_yonetim_bilesik_kaldirilmisti():
    """NAV-IA-04: render_yonetim_bilesik app.py'de tanımlı DEĞİL."""
    kod = (ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "render_yonetim_bilesik":
            assert False, "render_yonetim_bilesik hâlâ tanımlı — kaldırılmalı"


def test_force_auth_gate_integration():
    """NAV-IA-04: main() _force_auth_gate flagını kontrol eder."""
    kod = (ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    main_found = False
    has_flag_check = False
    has_popover_btn = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            main_found = True
            func_body = ast.unparse(node)
            has_flag_check = "_force_auth_gate" in func_body
            break

    assert main_found, "main() bulunamadı"
    assert has_flag_check, "main() _force_auth_gate flagını kontrol etmiyor"


def test_eski_url_guncel_mappings():
    """NAV-IA-04: eski_url_yonlendirme güncel."""
    from web_dashboard.tabs import eski_url_yonlendir

    assert eski_url_yonlendir("kimlik") == ("admin_auth", "")
    assert eski_url_yonlendir("yonetim") == ("admin_yonetim", "")
    assert eski_url_yonlendir("kullanicilar") == ("musteri_yonetimi", "kullanicilar")
