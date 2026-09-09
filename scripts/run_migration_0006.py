#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Migration 0006_nace_details.sql uygulayici (psycopg uzerinden)."""
import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_database_url  # noqa: E402

SQL_FILE = ROOT / "src" / "company_master" / "schema" / "migrations" / "0006_nace_details.sql"


def get_conn():
    url = get_database_url()
    if url.startswith("postgresql+psycopg://"):
        url = url.replace("postgresql+psycopg://", "postgresql://", 1)
    return psycopg.connect(url, prepare_threshold=None, autocommit=True)


def main():
    sql = SQL_FILE.read_text(encoding="utf-8-sig")
    conn = get_conn()
    with conn.cursor() as cur:
        # Sutun durumu (once)
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'companies'"
        )
        cols = {r[0] for r in cur.fetchall()}
        print("Mevcut nace sutunlari:", [c for c in cols if "nace" in c])

        # Migration calistir: once yorumlari temizle, sonra bos olmayanlari execute et
        for stmt in sql.split(";"):
            clean = "\n".join(
                ln for ln in stmt.splitlines() if not ln.strip().startswith("--")
            ).strip()
            if clean:
                cur.execute(clean)
                print("OK:", clean.splitlines()[0][:70])

        # Son durum
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'companies'"
        )
        cols2 = {r[0] for r in cur.fetchall()}
        print("Son nace sutunlari:", sorted(c for c in cols2 if "nace" in c))

    conn.close()
    print("Migration 0006_nace_details tamam!")


if __name__ == "__main__":
    main()