# -*- coding: utf-8 -*-
"""DB durum probu: VKN dolulugu + mersis kolonu kontrolu."""
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

e = get_engine()
c = e.connect()
print("tax_number dolu:", c.execute(text(
    "SELECT COUNT(*) FROM companies WHERE tax_number IS NOT NULL AND tax_number != ''"
)).scalar())
print("vkn ornek:", c.execute(text(
    "SELECT tax_number FROM companies WHERE tax_number IS NOT NULL AND tax_number != '' LIMIT 5"
)).fetchall())
cols = [r[0] for r in c.execute(text(
    "SELECT column_name FROM information_schema.columns WHERE table_name='companies'"
)).fetchall()]
print("mersis kolonu var mi:", [x for x in cols if "mersis" in x.lower()])
print("tum kolonlar:", cols)
c.close()
