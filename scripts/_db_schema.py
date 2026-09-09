# -*- coding: utf-8 -*-
"""companies tablosu index/schema bilgisi (geçici diyagnostik)."""
import sys

sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

e = get_engine()
c = e.connect()
print("--- unique index'ler ---")
for x in c.execute(text(
    "SELECT indexname, indexdef FROM pg_indexes WHERE tablename='companies'"
)).fetchall():
    print(x[0], "::", x[1])
print("--- toplam kayit ---")
print(c.execute(text("SELECT count(*) FROM companies")).scalar())
print("--- tax_number dolu / unique kontrol ---")
r = c.execute(text(
    "SELECT count(*) FILTER (WHERE tax_number IS NOT NULL), "
    "count(DISTINCT tax_number) FROM companies"
)).fetchone()
print("dolu:", r[0], "distinct:", r[1])
c.close()