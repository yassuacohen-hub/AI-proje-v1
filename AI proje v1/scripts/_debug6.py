import re
f = open("scripts/recalculate_quality_scores.py", "r", encoding="utf-8")
s = f.read()
f.close()
m = re.search(r"NEW_QUALITY_SQL = text\(\"\"\"(.+?)\"\"\"\)", s, re.DOTALL)
sql = m.group(1)
for i, line in enumerate(sql.split("\n")):
    if "THEN -" in line:
        print(f"{i+1}: {line.strip()}")
