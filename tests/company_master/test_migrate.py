"""Migration dosyaları ve çalıştırıcı için birim testleri.

Gerçek PostgreSQL gerektirmez: dosya sıralaması, sözdizimi (pglast varsa)
ve _split_statements davranışı doğrulanır.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.company_master.db import migrate


MIGRATIONS_DIR = migrate.MIGRATIONS_DIR


def test_migration_dosyalari_sirali_ve_numarali():
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    assert len(files) >= 4, "En az 4 migration dosyası bekleniyor"
    for f in files:
        assert re.match(r"^\d{4}_.+\.sql$", f.name), f"Geçersiz dosya adı: {f.name}"


def test_split_statements_yorumlari_atlar():
    sql = "-- yorum satırı\nCREATE TABLE t (id INT); -- son yorum\nSELECT 1;"
    stmts = migrate._split_statements(sql)
    assert stmts == ["CREATE TABLE t (id INT)", "SELECT 1"]


def test_split_statements_bos_sql():
    assert migrate._split_statements("-- sadece yorum\n") == []


def test_migration_sql_syntax_pglast():
    """pglast (libpg_query) ile gerçek PostgreSQL sözdizimi doğrulaması."""
    try:
        import pglast
    except ImportError:
        import pytest
        pytest.skip("pglast kurulu değil")

    for f in sorted(MIGRATIONS_DIR.glob("*.sql")):
        sql = f.read_text(encoding="utf-8")
        stmts = pglast.parse_sql(sql)  # hata fırlatırsa test düşer
        assert len(stmts) > 0, f"{f.name} boş görünüyor"


def test_core_tablolari_tanimli():
    """0001 çekirdek tabloları içerir."""
    sql = (MIGRATIONS_DIR / "0001_core.sql").read_text(encoding="utf-8")
    for table in ("companies", "osbs", "sources", "source_records", "quarantine_firms"):
        assert f"CREATE TABLE IF NOT EXISTS {table}" in sql, f"{table} eksik"


def test_tum_master_tablolari_kapsaniyor():
    """Ana belgedeki 19 tablo + Faz 1.2 tabloları migration'larda tanımlı."""
    beklenen = [
        "companies", "company_names", "company_identifiers", "company_locations",
        "osbs", "company_industries", "nace_codes", "company_products",
        "products", "product_categories", "company_contacts", "sources",
        "source_records", "entity_resolution", "evidence", "company_events",
        "company_state", "commercial_signals", "momentum_snapshot",
        "company_capabilities", "certifications", "key_personnel",
    ]
    tum_sql = ""
    for f in sorted(MIGRATIONS_DIR.glob("*.sql")):
        tum_sql += f.read_text(encoding="utf-8")
    for table in beklenen:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in tum_sql, f"{table} tanımlı değil"
