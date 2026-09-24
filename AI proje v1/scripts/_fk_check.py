# -*- coding: utf-8 -*-
"""companies tablosuna bagli FK referanslarini listeler."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

SQL = """
SELECT tc.table_name AS child_table,
       kcu.column_name AS fk_column,
       rc.delete_rule,
       rc.update_rule
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
  ON tc.constraint_name = ccu.constraint_name AND tc.table_schema = ccu.table_schema
JOIN information_schema.referential_constraints rc
  ON tc.constraint_name = rc.constraint_name AND tc.constraint_schema = rc.constraint_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND ccu.table_name = 'companies'
  AND tc.table_schema = 'public'
"""

engine = get_engine()
with engine.connect() as conn:
    rows = conn.execute(text(SQL)).fetchall()

if not rows:
    print("companies tablosuna bagli FK yok")
else:
    for child, col, drule, urule in rows:
        print(f"{child}.{col}  (delete_rule={drule})")
