# -*- coding: utf-8 -*-
"""DATA-LOG-01: Giriş etkinliği + arama kaydı testleri.

Kapsam:
- _mask_ip / _mask_email yardimcilari
- _log_login_event fonksiyonu
- _log_search_event fonksiyonu
- login_events / search_events tablolari (migration ile olusturulmus)
- API endpoint'lerinde kayit (mock'lu)
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ------------------------------------------------------------------- yardimcilar


def test_mask_ip_last_octet():
    """IP son oktesi maskelenmeli."""
    from web_app import _dl_mask_ip

    assert _dl_mask_ip("192.168.1.134") == "192.168.1.0"
    assert _dl_mask_ip("10.0.0.1") == "10.0.0.0"
    assert _dl_mask_ip("127.0.0.1") == "127.0.0.0"


def test_mask_ip_invalid():
    """Gecersiz IP geri donmeli."""
    from web_app import _dl_mask_ip

    assert _dl_mask_ip("abc") == "abc"
    assert _dl_mask_ip("1.2.3") == "1.2.3"


def test_mask_email():
    """E-posta maskelenmeli: admin@huginn.local -> ad***@huginn.local."""
    from web_app import _mask_email

    assert _mask_email("admin@huginn.local") == "ad***@huginn.local"
    assert _mask_email("test@example.com") == "te***@example.com"


def test_mask_email_no_at():
    """@ icermeyen e-posta donerildi (KVKK yardimcisi)."""
    from web_app import _mask_email

    assert _mask_email("notanemail") == "notanemail"


# ------------------------------------------------------------------- fonksiyonlar


def test_log_login_event_fonksiyonu_var():
    """_log_login_event app.py'de tanımlı."""
    kod = Path("web_app.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    found = False
    has_params = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_log_login_event":
            found = True
            func_body = ast.unparse(node)
            has_params = "login_events" in func_body and "email_masked" in func_body
            break

    assert found, "_log_login_event bulunamadı"
    assert has_params, "_log_login_event INSERT INTO login_events içermiyor"


def test_log_search_event_fonksiyonu_var():
    """_log_search_event app.py'de tanımlı."""
    kod = Path("web_app.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    found = False
    has_params = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_log_search_event":
            found = True
            func_body = ast.unparse(node)
            has_params = "search_events" in func_body and "query" in func_body
            break

    assert found, "_log_search_event bulunamadı"
    assert has_params, "_log_search_event INSERT INTO search_events içermiyor"


def test_login_endpoint_logs_event():
    """api_buyer/login basarili cikisinda _log_login_event cagiriyor."""
    kod = Path("web_app.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    login_found = False
    has_log = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "api_buyer_login":
            login_found = True
            func_body = ast.unparse(node)
            has_log = "_log_login_event(" in func_body
            break

    assert login_found, "api_buyer_login bulunamadı"
    assert has_log, "api_buyer_login _log_login_event cagirmiyor"


def test_companies_endpoint_logs_search():
    """/api/companies arama durumunda _log_search_event cagiriyor."""
    kod = Path("web_app.py").read_text(encoding="utf-8")
    tree = ast.parse(kod)

    companies_found = False
    has_log = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "api_companies":
            companies_found = True
            func_body = ast.unparse(node)
            has_log = "_log_search_event(" in func_body
            break

    assert companies_found, "api_companies bulunamadı"
    assert has_log, "api_companies _log_search_event cagirmiyor"


# ------------------------------------------------------------------- migration


def test_migration_0015_exists():
    """0015_data_log.sql dosyasi mevcut."""
    assert (
        Path("src/company_master/schema/migrations/0015_data_log.sql").exists()
    ), "0015_data_log.sql bulunamadı"


def test_migration_0015_has_both_tables():
    """Migration hem login_events hem search_events tablosunu olusturuyor."""
    sql = Path("src/company_master/schema/migrations/0015_data_log.sql").read_text(
        encoding="utf-8"
    )
    assert "CREATE TABLE IF NOT EXISTS login_events" in sql
    assert "CREATE TABLE IF NOT EXISTS search_events" in sql


def test_migration_0015_kvkk_masking():
    """Migration KVKK icin ip_masked ve email_masked sütunlari icermeli."""
    sql = Path("src/company_master/schema/migrations/0015_data_log.sql").read_text(
        encoding="utf-8"
    )
    assert "email_masked" in sql
    assert "ip_masked" in sql


def test_migration_0015_sqlite_compatible():
    """Migration SQLite uyumlu SQL kullanmali (UUID yoksa)."""
    sql = Path("src/company_master/schema/migrations/0015_data_log.sql").read_text(
        encoding="utf-8"
    )
    assert "UUID" not in sql.upper() or "gen_random_uuid" not in sql
    assert "CURRENT_TIMESTAMP" in sql


def test_migration_0015_in_versions():
    """schema_versions.json'da version 15 entry mevcut."""
    import json

    versions = json.loads(
        Path("src/company_master/schema/migrations/schema_versions.json")
        .read_text(encoding="utf-8")
    )
    assert versions["current_version"] >= 13
    assert any(m["version"] == 15 for m in versions["migrations"])


def test_migrate_py_target_15():
    """migrate.py default target 15 olmalı."""
    kod = Path("src/company_master/schema/migrations/migrate.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(kod)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_migrations":
            func_body = ast.unparse(node)
            assert "15" in func_body, "run_migrations target 15 yoksa"
            break
    else:
        assert False, "run_migrations fonksiyonu bulunamadı"


# ------------------------------------------------------------------- musteri_yonetimi


def test_musteri_yonetimi_giris_aktinligi_real():
    """_giris_aktinligi login_events tablosunu sorguluyor."""
    kod = Path("web_dashboard/tabs/musteri_yonetimi.py").read_text(encoding="utf-8")
    assert "login_events" in kod
    assert "_giris_aktinligi" in kod


def test_musteri_yonetim_aramalar_real():
    """_aramalar search_events tablosunu sorguluyor."""
    kod = Path("web_dashboard/tabs/musteri_yonetimi.py").read_text(encoding="utf-8")
    assert "search_events" in kod
    assert "_aramalar" in kod


# ------------------------------------------------------------------- api_event_count


def test_data_log_function_count():
    """app.py'de login + search event logging cagirlari sayisi uygun."""
    kod = Path("app.py").read_text(encoding="utf-8") if Path("app.py").exists() else ""
    web_kod = Path("web_app.py").read_text(encoding="utf-8")

    # web_app.py'de en az 5 login event cagri + 1 search event cagri olmalı
    login_calls = web_kod.count("_log_login_event(")
    search_calls = web_kod.count("_log_search_event(")

    assert login_calls >= 5, f"login event cagri sayisi yeterli degil: {login_calls}"
    assert search_calls >= 1, f"search event cagri sayisi yeterli degil: {search_calls}"
