# -*- coding: utf-8 -*-
"""P1-5 diyagnostik: source_records semasi + NACE'siz kayitlar."""
import sys

sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

e = get_engine()
c = e.connect()
cols = [x[0] for x in c.execute(text(
    "SELECT column_name FROM information_schema.columns "
    "WHERE table_name='source_records' ORDER BY ordinal_position"
)).fetchall()]
print("source_records kolonlari:", ", ".join(cols))
print("NACE'siz toplam:", c.execute(
    text("SELECT count(*) FROM companies WHERE nace_code IS NULL")).scalar())
print("NACE'siz source_record_id dolu:", c.execute(
    text("SELECT count(*) FROM companies WHERE nace_code IS NULL "
         "AND source_record_id IS NOT NULL")).scalar())
print("NACE'siz source_record_id bos:", c.execute(
    text("SELECT count(*) FROM companies WHERE nace_code IS NULL "
         "AND source_record_id IS NULL")).scalar())
# Ornek: NACE'siz 5 kayit
print("\nOrnek NACE'siz kayitlar:")
for x in c.execute(text(
    "SELECT trade_name, source_record_id FROM companies "
    "WHERE nace_code IS NULL ORDER BY created_at DESC LIMIT 5"
)).fetchall():
    print(" -", x[0], "|", x[1])
# source_records ornek satir (kolon bilgisi)
print("\nsource_records ilk satir:")
for x in c.execute(text("SELECT * FROM source_records LIMIT 1")).fetchall():
    print(dict(x._mapping) if hasattr(x, "_mapping") else x)
c.close()