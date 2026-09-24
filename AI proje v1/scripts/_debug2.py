import sys, re
sys.path.insert(0, "src")
from sqlalchemy import text
from company_master.db.connection import get_engine

f = open("scripts/recalculate_quality_scores.py", "r", encoding="utf-8")
s = f.read()
f.close()

m = re.search(r"NEW_QUALITY_SQL = text\(\"\"\"(.+?)\"\"\"\)", s, re.DOTALL)
sql = m.group(1)

# extract just the SELECT expression from the CTE
start = sql.index("SELECT")
end = sql.index("FROM companies c")
select_expr = sql[start:end].strip()

engine = get_engine()
conn = engine.connect()
q = "SELECT AVG(" + select_expr + ") FROM companies c LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id WHERE c.is_ankara = TRUE"
avg = conn.execute(text(q)).scalar()
print("script select avg:", avg)
conn.close()
