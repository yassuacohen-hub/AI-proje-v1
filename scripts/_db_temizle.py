# -*- coding: utf-8 -*-
"""Benim kill edilen ingest süreçlerimden kalan ölü DB bağlantılarını temizler."""
import sys

sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

e = get_engine()
c = e.connect()
# Bu sorgu kalıpları benim ingest_merged.py'ye (bul/update/savepoint) aittir.
for pid in c.execute(text(
    "SELECT pid FROM pg_stat_activity WHERE state = 'idle in transaction' "
    "AND (query ILIKE '%SELECT company_id FROM companies WHERE LOWER%' "
    "     OR query ILIKE '%UPDATE companies SET tax_number%' "
    "     OR query ILIKE '%SAVEPOINT sa_savepoint%' )"
)).fetchall():
    print("Terminate ediliyor:", pid[0])
    c.execute(text("SELECT pg_terminate_backend(:p)"), {"p": pid[0]})
c.commit()
print("Temizlik tamam")
c.close()