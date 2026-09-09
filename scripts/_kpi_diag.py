# -*- coding: utf-8 -*-
"""companies KPI diyagnostiği."""
import sys

sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

e = get_engine()
c = e.connect()
cols = [x[0] for x in c.execute(text(
    "SELECT column_name FROM information_schema.columns "
    "WHERE table_name='companies' ORDER BY ordinal_position"
)).fetchall()]
print("KOLONLAR:", ", ".join(cols))
print("Toplam:", c.execute(text("SELECT count(*) FROM companies")).scalar())
print("NACE li:", c.execute(text(
    "SELECT count(*) FROM companies WHERE nace_code IS NOT NULL")).scalar())
print("VKN li:", c.execute(text(
    "SELECT count(*) FROM companies WHERE tax_number IS NOT NULL")).scalar())
print("Web li:", c.execute(text(
    "SELECT count(*) FROM companies WHERE website_domain IS NOT NULL")).scalar())
if "adres" in cols:
    print("Adres li:", c.execute(text(
        "SELECT count(*) FROM companies WHERE adres IS NOT NULL")).scalar())
if "primary_address" in cols:
    print("primary_address li:", c.execute(text(
        "SELECT count(*) FROM companies WHERE primary_address IS NOT NULL")).scalar())
c.close()