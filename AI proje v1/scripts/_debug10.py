import sys, re
sys.path.insert(0, "src")
from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
conn = engine.connect()

f = open("scripts/recalculate_quality_scores.py", "r", encoding="utf-8")
s = f.read()
f.close()
m = re.search(r"NEW_QUALITY_SQL = text\(\"\"\"(.+?)\"\"\"\)", s, re.DOTALL)
sql = m.group(1)

# Replace parameters with literals
sql = sql.replace("->>:adres", "->>'adres'")
sql = sql.replace("->>:sektor", "->>'sektor'")
sql = sql.replace("->>:nace_code", "->>'nace_code'")
sql = sql.replace("->>:osb_parsel", "->>'osb_parsel'")

print("first 300 chars of SQL:")
print(sql[:300])
print("...")

# Run the literal SQL
result = conn.execute(text(sql))
print("updated:", result.rowcount)
avg = conn.execute(text("SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE")).scalar()
print("avg:", avg)
conn.close()
