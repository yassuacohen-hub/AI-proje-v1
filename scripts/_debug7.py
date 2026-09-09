import sys, re
sys.path.insert(0, "src")
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

f = open("scripts/recalculate_quality_scores.py", "r", encoding="utf-8")
s = f.read()
f.close()
m = re.search(r"NEW_QUALITY_SQL = text\(\"\"\"(.+?)\"\"\"\)", s, re.DOTALL)
sql = m.group(1)
t = text(sql)
compiled = t.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
print(str(compiled)[:2000])
print("...")
print(str(compiled)[-500:])
