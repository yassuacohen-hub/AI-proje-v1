#!/usr/bin/env python3
"""
Migration Testleri — v0016 ↔ v0017
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import db_migrate


def test_migration_files_exist():
    """Migration dosyalarının varlığını test et."""
    migrations_dir = Path(__file__).resolve().parents[1] / "src" / "company_master" / "schema" / "migrations"

    # Up dosyaları
    assert (migrations_dir / "0016_users_last_login.sql").exists()
    assert (migrations_dir / "0017_user_activity_log.sql").exists()

    # Down dosyaları — VERI-04 kanonik yol: migrations/down/NNNN_ad.down.sql
    assert (migrations_dir / "down" / "0016_users_last_login.down.sql").exists()
    assert (migrations_dir / "down" / "0017_user_activity_log.down.sql").exists()

    print("[TEST] migration_files_exist: PASSED")


def test_read_migration_file():
    """Migration dosyası okuma testi."""
    # 0017 up
    sql_up = db_migrate.read_migration_file("0017", "up")
    assert "CREATE TABLE IF NOT EXISTS user_activity_log" in sql_up
    assert "BIGSERIAL PRIMARY KEY" in sql_up
    assert "REFERENCES users(user_id)" in sql_up
    assert "CHECK (olay_tipi IN" in sql_up
    assert "INET NULL" in sql_up
    assert "CHAR(2) NULL" in sql_up
    assert "idx_activity_user_zaman" in sql_up
    assert "idx_activity_tip_zaman" in sql_up

    # 0017 down
    sql_down = db_migrate.read_migration_file("0017", "down")
    assert "DROP INDEX IF EXISTS idx_activity_tip_zaman" in sql_down
    assert "DROP INDEX IF EXISTS idx_activity_user_zaman" in sql_down
    assert "DROP TABLE IF EXISTS user_activity_log" in sql_down

    print("[TEST] read_migration_file: PASSED")


def test_migration_file_structure():
    """Migration dosyalarının yapısal doğrulaması."""
    migrations_dir = Path(__file__).resolve().parents[1] / "src" / "company_master" / "schema" / "migrations"

    # 0017 up içeriği
    up_content = (migrations_dir / "0017_user_activity_log.sql").read_text(encoding="utf-8")
    lines = [l.strip() for l in up_content.splitlines() if l.strip() and not l.strip().startswith("--")]

    # Temel yapı kontrolleri
    assert any("CREATE TABLE" in l for l in lines)
    assert any("user_activity_log" in l for l in lines)
    assert any("BIGSERIAL" in l for l in lines)
    assert any("UUID" in l for l in lines)
    assert any("olay_tipi" in l for l in lines)
    assert any("CHECK" in l for l in lines)
    assert any("INDEX" in l for l in lines)

    print("[TEST] migration_file_structure: PASSED")


def test_db_migrate_import():
    """db_migrate modülü import edilebiliyor mu."""
    import scripts.db_migrate as db_migrate_module
    assert hasattr(db_migrate_module, "migrate")
    assert hasattr(db_migrate_module, "get_db_url")
    assert hasattr(db_migrate_module, "read_migration_file")
    assert hasattr(db_migrate_module, "verify_table_exists")

    print("[TEST] db_migrate_import: PASSED")


def test_prod_runbook_exists():
    """Prod runbook scripti var mı."""
    runbook = Path(__file__).resolve().parents[1] / "scripts" / "db_migrate_prod.sh"
    assert runbook.exists()

    content = runbook.read_text(encoding="utf-8")
    assert "PROD_DATABASE_URL" in content
    assert "0017_user_activity_log" in content
    assert "pg_dump" in content
    assert "pg_isready" in content
    assert "ROLLBACK" in content.upper() or "rollback" in content.lower()

    print("[TEST] prod_runbook_exists: PASSED")


def test_alertmanager_rules_exist():
    """AlertManager kural dosyası var mı."""
    rules_file = Path(__file__).resolve().parents[1] / "monitoring" / "alertmanager" / "migration_rules.yml"
    assert rules_file.exists()

    content = rules_file.read_text(encoding="utf-8")
    assert "MigrationReplicationLagHigh" in content
    assert "MigrationTableMissing" in content
    assert "ActivityLogWriteRateLow" in content
    assert "user_activity_log" in content

    print("[TEST] alertmanager_rules_exist: PASSED")


if __name__ == "__main__":
    test_migration_files_exist()
    test_read_migration_file()
    test_migration_file_structure()
    test_db_migrate_import()
    test_prod_runbook_exists()
    test_alertmanager_rules_exist()
    print("\n[TUM TESTLER GECTI]")
