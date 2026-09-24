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

# Find the UPDATE part
idx = sql.rfind("UPDATE companies")
update_sql = sql[idx:]
cte_sql = sql[:idx]

print("CTE length:", len(cte_sql))
print("UPDATE length:", len(update_sql))
print("UPDATE start:", update_sql[:200])

# First test: run CTE as SELECT
rows = conn.execute(text(cte_sql + " SELECT company_id, new_score FROM scored LIMIT 5")).fetchall()
print("CTE scores:", [r[1] for r in rows])

# Then run UPDATE
result = conn.execute(text(cte_sql + " " + update_sql))
conn.commit()
print("updated:", result.rowcount)
avg = conn.execute(text("SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE")).scalar()
print("avg:", avg)
conn.close()
