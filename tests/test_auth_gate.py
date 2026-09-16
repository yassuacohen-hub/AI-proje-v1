# -*- coding: utf-8 -*-
"""AUTH-GATE-01: Giriş kapısı modalı testleri.

Kapsam:
- POST /api/admin/login endpoint'i (JSON body)
- POST /api/admin/reset-request endpoint'i
- POST /api/admin/reset-confirm endpoint'i
- app.py auth gate (Modal kapatilamaz)
- Modal kapatilabilir parametresi
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


def test_admin_login_post_endpoint():
    """POST /api/admin/login JSON body ile çalışır."""
    import ast

    kod = Path("web_app.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    post_login = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "api_admin_login_post":
            post_login = True
            func_body = ast.unparse(node)
            assert "email" in func_body
            assert "password" in func_body
            assert "token" in func_body
            break

    assert post_login, "api_admin_login_post bulunamadı"


def test_admin_reset_request_endpoint():
    """POST /api/admin/reset-request endpoint'i var."""
    import ast

    kod = Path("web_app.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "api_admin_reset_request":
            found = True
            break
    assert found, "api_admin_reset_request bulunamadı"


def test_admin_reset_confirm_endpoint():
    """POST /api/admin/reset-confirm endpoint'i var."""
    import ast

    kod = Path("web_app.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "api_admin_reset_confirm":
            found = True
            break
    assert found, "api_admin_reset_confirm bulunamadı"


def test_auth_modal_icerik_fonksiyonu():
    """app.py _auth_modal_icerik fonksiyonu var."""
    import ast

    kod = Path("app.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_auth_modal_icerik":
            found = True
            func_body = ast.unparse(node)
            assert "render_admin_login" in func_body
            assert "Misafir" in func_body or "misafir" in func_body
            assert "Şifremi unuttum" in func_body or "sifre_unuttum" in func_body
            break

    assert found, "_auth_modal_icerik bulunamadı"


def test_modal_dismissible_parametresi():
    """Modal.streamlit() dismissible=not kapatilabilir gönderir."""
    import ast

    kod = Path("src/company_master/ui/components/modal.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "streamlit":
            func_body = ast.unparse(node)
            assert "dismissible" in func_body
            found = True
            break

    assert found, "Modal.streamlit dismissible parametresi yok"


def test_admin_auth_post_kullanimi():
    """admin_auth.py POST /api/admin/login kullanıyor."""
    kod = Path("web_dashboard/tabs/admin_auth.py").read_text(encoding="utf-8")
    assert "post_api(\"/api/admin/login\"" in kod or "post_api('/api/admin/login'" in kod
    assert "get_api" not in kod, "get_api hala kullanılıyor"