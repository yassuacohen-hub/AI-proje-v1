# -*- coding: utf-8 -*-
"""test_admin_sessiz_except.py — Sessiz `except Exception: pass` tespit testleri.

Admin sekmelerindeki sessiz `except Exception: pass` kalıplarının
temizlendiğini ve AST tespit aracının çalıştığını doğrular.
"""
from __future__ import annotations

import ast
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Test modülünü import et
sys.path.insert(0, str(ROOT / "scripts"))
import detect_silent_except as dse


# Test verileri: sessiz except içeren örnek kod
SILENT_EXCEPT_CODE = '''
def func1():
    try:
        x = 1 / 0
    except Exception:
        pass

def func2():
    try:
        do_something()
    except Exception as e:
        pass

def func3():
    try:
        risky()
    except (ValueError, Exception) as e:
        pass

def func4():
    try:
        pass
    except:
        pass
'''

NON_SILENT_EXCEPT_CODE = '''
def func1():
    try:
        x = 1 / 0
    except Exception as e:
        logger.warning("Hata", exc_info=e)
        return None

def func2():
    try:
        do_something()
    except ValueError as e:
        logger.warning("Hata: %s", e)
        raise
'''

MIXED_CODE = '''
def func1():
    try:
        x = 1 / 0
    except Exception:
        pass

def func2():
    try:
        do_something()
    except Exception as e:
        logger.warning("Hata", exc_info=e)
        return None
'''


def test_silent_except_detection():
    """Sessiz except: pass kalıplarının tespit edildiğini doğrula."""
    tree = ast.parse(SILENT_EXCEPT_CODE)
    visitor = dse.SilentExceptVisitor()
    visitor.visit(tree)

    # 4 sessiz except: pass kalıbı olmalı
    assert len(visitor.silent_excepts) == 4, f"Beklenen 4, bulundu {len(visitor.silent_excepts)}"

    # Tüm satır numaraları kontrol edilsin (docstring ve boş satırlar nedeniyle offsetli)
    lines = {item["lineno"] for item in visitor.silent_excepts}
    # Gerçek satır numaraları: 5, 11, 17, 23 (docstring + boş satır offset)
    assert lines == {5, 11, 17, 23}, f"Beklenen {{5, 11, 17, 23}}, bulundu {lines}"


def test_non_silent_except_not_detected():
    """Loglama/yakalama yapan except'lerin sessiz olarak işaretlenmediğini doğrula."""
    tree = ast.parse(NON_SILENT_EXCEPT_CODE)
    visitor = dse.SilentExceptVisitor()
    visitor.visit(tree)

    # Sessiz except tespit edilmemeli
    assert len(visitor.silent_excepts) == 0, (
        f"Sessiz except tespit edilmedi ama bulundu: {visitor.silent_excepts}"
    )


def test_mixed_code():
    """Hem sessiz hem loglayan except içeren karışık kod."""
    tree = ast.parse(MIXED_CODE)
    visitor = dse.SilentExceptVisitor()
    visitor.visit(tree)

    # Sadece 1 sessiz except (func1) tespit edilmeli
    assert len(visitor.silent_excepts) == 1
    assert visitor.silent_excepts[0]["lineno"] == 5


def test_bare_except_detected():
    """`except:` (bare except) da tespit edilmeli."""
    code = '''
def func():
    try:
        pass
    except:
        pass
'''
    tree = ast.parse(code)
    visitor = dse.SilentExceptVisitor()
    visitor.visit(tree)
    assert len(visitor.silent_excepts) == 1


def test_except_with_other_statements_not_silent():
    """`pass` dışında statement içeren except sessiz sayılmamalı."""
    code = '''
def func():
    try:
        pass
    except Exception:
        logger.error("Hata")
        pass
'''
    tree = ast.parse(code)
    visitor = dse.SilentExceptVisitor()
    visitor.visit(tree)
    # pass dışında logger.error çağrısı var, sessiz sayılmamalı
    assert len(visitor.silent_excepts) == 0


def test_detect_silent_excepts_in_file():
    """Dosya bazlı tespit fonksiyonu çalışıyor mu?"""
    import tempfile
    from pathlib import Path

    # Test kodu - başında boş satır yok, doğrudan fonksiyon başlıyor
    test_code = '''def func():
    try:
        pass
    except Exception:
        pass
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        temp_path = Path(f.name)

    try:
        results = dse.find_silent_excepts_in_file(Path(f.name))
        assert len(results) == 1, f"Beklenen 1, bulundu {len(results)}"
        # AST satır numarası 4 oluyor (def satırı 1, try 2, except 3, pass 4, except sonu 5)
        assert results[0]["lineno"] in (3, 4), f"Beklenen 3-4 arası, bulundu {results[0]['lineno']}"
    finally:
        Path(f.name).unlink()


def test_admin_tabs_no_silent_excepts():
    """Admin sekmelerinde sessiz except kalmamalı (tüm fix sonrası)."""
    results = dse.find_all_silent_excepts()

    # Admin sekmesi dosyalarında sessiz except kalmamalı
    admin_files = [
        "web_dashboard/tabs/admin_kpi.py",
        "web_dashboard/tabs/admin_quality.py",
        "web_dashboard/tabs/admin_performance.py",
        "web_dashboard/tabs/admin_api_analytics.py",
    ]

    for admin_file in admin_files:
        if admin_file in dse.find_all_silent_excepts():
            issues = dse.find_all_silent_excepts()[admin_file]
            # Sadece ImportError fallback kalabilir (plotly fallback)
            silent_excepts = [
                i for i in issues
                if not (isinstance(i, dict) and "ImportError" in str(i.get("message", "")))
            ]
            assert len(silent_excepts) == 0, (
                f"{admin_file} dosyasında sessiz except bulundu: {silent_excepts}"
            )


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
