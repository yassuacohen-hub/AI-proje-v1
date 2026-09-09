#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Minimal enrichment script - raw psycopg kullanir.
Supabase pgbouncer hatasi icin.
"""
import json
import sys
from pathlib import Path
import psycopg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.db.connection import get_database_url

def get_conn():
    url = get_database_url()
    # postgresql:// veya postgresql+psycopg:// prefixini kaldir
    for prefix in ("postgresql+psycopg://", "postgresql://"):
        if url.startswith(prefix):
            url = url[len(prefix):]
    return psycopg.connect(url, prepare_threshold=None, autocommit=True)

print("Enrichment baslatiliyor...")
conn = get_conn()
with conn.cursor() as cur:
    # Mevcut veri durumu
    cur.execute("SELECT COUNT(*) FROM companies")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM companies WHERE vergi_no IS NOT NULL")
    vergi = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM companies WHERE osb_parsel IS NOT NULL")
    parsel = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM companies WHERE website_domain IS NOT NULL")
    web = cur.fetchone()[0]
    print(f"Toplam: {total}, Vergi: {vergi}, Parsel: {parsel}, Web: {web}")
conn.close()
print("Tamam!")