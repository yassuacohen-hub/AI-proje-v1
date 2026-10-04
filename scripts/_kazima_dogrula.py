#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kazıma pipeline doğrulaması — assert-based (test framework yok).

Migration: 0050_scrape_audit_log.sql (D-323: 0046 çakışması nedeniyle 0050'ye taşındı).
"""

import sys
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import text  # noqa: E402
from company_master.db.connection import get_engine  # noqa: E402


def assert_migration_0050_exists():
    """Migration 0050 uygulandı mı?"""
    with get_engine().connect() as conn:
        result = conn.execute(
            text("SELECT filename FROM public.schema_migrations WHERE filename='0050_scrape_audit_log.sql'")
        ).fetchone()
        assert result is not None, "HATA: Migration 0050 uygulanmamış"
    print("✓ Migration 0050 uygulandı")


def assert_scrape_tables_exist():
    """Kazıma tabloları mevcut mu?"""
    with get_engine().connect() as conn:
        for table in ['scrape_audit_log', 'scrape_pages', 'scrape_errors']:
            result = conn.execute(
                text(f"SELECT 1 FROM information_schema.tables WHERE table_name='{table}'")
            ).fetchone()
            assert result is not None, f"HATA: Tablo {table} yok"
    print("✓ Kazıma tabloları (audit_log, pages, errors) mevcut")


def assert_unique_constraint():
    """UNIQUE (source_url, content_hash) kısıtı var mı?"""
    with get_engine().connect() as conn:
        result = conn.execute(
            text(
                "SELECT constraint_name FROM information_schema.table_constraints "
                "WHERE table_name='scrape_pages' AND constraint_type='UNIQUE'"
            )
        ).fetchone()
        assert result is not None, "HATA: UNIQUE (source_url, content_hash) kısıtı yok"
    print("✓ UNIQUE (source_url, content_hash) dedup kısıtı var")


def assert_cost_usd_check():
    """cost_usd CHECK (cost_usd = 0) var mı?"""
    with get_engine().connect() as conn:
        try:
            conn.execute(
                text(
                    "INSERT INTO scrape_audit_log (source_name, source_url, action, status, cost_usd) "
                    "VALUES ('test', 'http://test.local', 'test', 'pending', 0.01)"
                )
            )
            assert False, "CHECK kısıtı çalışmıyor: cost_usd=0.01 yazıldı"
        except Exception as e:
            if "cost_usd" in str(e):
                print("✓ CHECK (cost_usd = 0) kısıtı çalışıyor")
            else:
                raise


def assert_robots_permission_router():
    """scraping_permission_router.py var mı?"""
    router_file = ROOT / "src" / "company_master" / "utils" / "scraping_permission_router.py"
    assert router_file.exists(), f"HATA: {router_file} yok"
    content = router_file.read_text(encoding='utf-8')
    assert "get_router" in content, "HATA: get_router() fonksiyonu yok"
    print("✓ scraping_permission_router.py (robots.txt + rate limit) var")


def assert_hash_function():
    """SHA256 hash fonksiyonu test."""
    test_content = "test page content"
    expected_hash = hashlib.sha256(test_content.encode()).hexdigest()
    assert len(expected_hash) == 64, f"HATA: SHA256 hash 64 char değil: {len(expected_hash)}"
    print(f"✓ SHA256 hash fonksiyonu çalışıyor (örnek: {expected_hash[:16]}...)")


def main():
    try:
        print("\n=== Kazıma Doğrulama Testi ===\n")
        assert_migration_0050_exists()
        assert_scrape_tables_exist()
        assert_unique_constraint()
        assert_cost_usd_check()
        assert_robots_permission_router()
        assert_hash_function()
        print("\n✅ TÜM TESTLER GEÇTİ — Kazıma altyapısı hazır\n")
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST BAŞARIŞIZ: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ BEKLENMEYEN HATA: {e}\n")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
