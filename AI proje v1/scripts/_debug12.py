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

sql = sql.replace("->>:adres", "->>'adres'")
sql = sql.replace("->>:sektor", "->>'sektor'")
sql = sql.replace("->>:nace_code", "->>'nace_code'")
sql = sql.replace("->>:osb_parsel", "->>'osb_parsel'")

# Extract scored CTE
scode_start = sql.index("WITH scored AS (")
scode_end = sql.index(") UPDATE companies")
scored_sql = sql[scode_start:scode_end] + ")"

print("Testing CTE alone...")
rows = conn.execute(text(scored_sql + " SELECT * FROM scored LIMIT 3")).fetchall()
for r in rows:
    print(r[:3])

print("\nRunning full UPDATE...")
result = conn.execute(text(scored_sql + " UPDATE companies c SET data_quality_score = GREATEST(0, LEAST(100, scored.new_score)) FROM scored WHERE c.company_id = scored.company_id"))
conn.commit()
print("updated:", result.rowcount)
avg = conn.execute(text("SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE")).scalar()
print("avg:", avg)
conn.close()
