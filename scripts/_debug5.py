import sys
sys.path.insert(0, "src")
from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
conn = engine.connect()

# Read the script's SQL
f = open("scripts/recalculate_quality_scores.py", "r", encoding="utf-8")
s = f.read()
f.close()

import re
m = re.search(r"NEW_QUALITY_SQL = text\(\"\"\"(.+?)\"\"\"\)", s, re.DOTALL)
sql = m.group(1)

print("Running script SQL directly...")
result = conn.execute(text(sql), {"adres": "adres", "sektor": "sektor", "nace_code": "nace_code", "osb_parsel": "osb_parsel"})
print("updated:", result.rowcount)
avg = conn.execute(text("SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE")).scalar()
print("avg after direct exec:", avg)
conn.close()
