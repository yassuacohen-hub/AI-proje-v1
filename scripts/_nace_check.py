# -*- coding: utf-8 -*-
"""nace_source check constraint degerlerini bul."""
import sys
sys.path.insert(0, "src")
from sqlalchemy import text
from company_master.db.connection import get_engine
e = get_engine(); c = e.connect()
# constraint degerleri
for x in c.execute(text(
    "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint "
    "WHERE conname LIKE '%nace_source%'"
)).fetchall():
    print(x[0])
    print(x[1])
# mevcut farkli degerler
print("--- mevcut nace_source degerleri ---")
for x in c.execute(text(
    "SELECT nace_source, count(*) FROM companies GROUP BY nace_source ORDER BY 2 DESC"
)).fetchall():
    print(repr(x[0]), x[1])
c.close()