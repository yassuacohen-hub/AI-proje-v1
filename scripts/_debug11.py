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

# Split into CTE and UPDATE parts
cte_part = "WITH scored AS (" + sql.split("WITH scored AS (")[1].split(") UPDATE")[0] + ") SELECT * FROM scored LIMIT 5"
update_part = sql.split(") UPDATE")[1]

print("CTE sample:")
for r in conn.execute(text(cte_part)).fetchall():
    print(r[:3])

print("\nRunning UPDATE...")
conn.execute(text("WITH scored AS (" + sql.split("WITH scored AS (")[1].split(") UPDATE")[0] + ") UPDATE companies c SET data_quality_score = GREATEST(0, LEAST(100, scored.new_score)) FROM scored WHERE c.company_id = scored.company_id"))
conn.commit()
avg = conn.execute(text("SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE")).scalar()
print("avg after split exec:", avg)
conn.close()
