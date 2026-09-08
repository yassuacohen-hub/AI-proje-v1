"""Ankara + OSB veri filtreleme entegrasyon testi."""

import sys
import os
import tempfile
from pathlib import Path

# Geçici SQLite DB
TEST_DIR = Path(tempfile.mkdtemp(prefix="company_master_test_"))
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DIR}/test.db"

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.company_master.db import init_db, get_engine
from src.company_master.seed.seed_ankara_osb import (
    generate_osb_master, generate_osb_firm, generate_non_osb_or_outside_ankara
)


def test_init_db_creates_companies():
    init_db()
    # Basit doğrulama
    import sqlite3
    db_path = TEST_DIR / "test.db"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('companies', 'osbs', 'quarantine_firms')")
    tables = {row[0] for row in cur.fetchall()}
    conn.close()
    assert "companies" in tables
    assert "osbs" in tables
    assert "quarantine_firms" in tables


def test_osb_master_count():
    osbs = generate_osb_master()
    assert len(osbs) == 9
    assert all(osb["city"] == "Ankara" for osb in osbs)
    assert any("OSTİM" in osb["name"] for osb in osbs)
    assert any("İvedik" in osb["name"] for osb in osbs)


def test_osb_firm_has_ankara_flag():
    osbs = generate_osb_master()
    firms = generate_osb_firm(osbs[0]["osb_id"], 5)
    for firm in firms:
        assert firm["is_ankara"] is True
        assert firm["is_osb_member"] is True
        assert firm["osb_id"] == osbs[0]["osb_id"]


def test_quarantine_records_marked():
    quarantine = generate_non_osb_or_outside_ankara(20)
    for record in quarantine:
        # ya Ankara değil ya OSB üyesi değil
        assert not (record["is_ankara"] and record["is_osb_member"])
        assert record["quarantine_reason"] is not None


def test_mvp_filter_logic():
    """MVP sorgusu: yalnız Ankara + OSB üyesi firmalar."""
    osbs = generate_osb_master()
    valid_firms = []
    invalid_firms = []
    for osb in osbs[:2]:  # 2 OSB
        valid_firms.extend(generate_osb_firm(osb["osb_id"], 5))
    invalid_firms.extend(generate_non_osb_or_outside_ankara(10))
    
    mvp_filter = [f for f in valid_firms if f["is_ankara"] and f["is_osb_member"]]
    assert len(mvp_filter) == len(valid_firms)  # hepsi geçerli
    assert all(f["quarantine_reason"] is None for f in mvp_filter)


if __name__ == "__main__":
    test_init_db_creates_companies()
    print("OK: test_init_db_creates_companies")
    test_osb_master_count()
    print("OK: test_osb_master_count")
    test_osb_firm_has_ankara_flag()
    print("OK: test_osb_firm_has_ankara_flag")
    test_quarantine_records_marked()
    print("OK: test_quarantine_records_marked")
    test_mvp_filter_logic()
    print("OK: test_mvp_filter_logic")
    print("\nTüm testler geçti.")