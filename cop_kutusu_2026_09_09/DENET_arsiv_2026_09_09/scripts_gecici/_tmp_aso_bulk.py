import json, sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text
engine = get_engine()
conn = engine.connect()

with open("data/aso/aso_full.jsonl", "r", encoding="utf-8") as f:
    aso = [json.loads(l) for l in f if l.strip()]

rows = conn.execute(text("SELECT company_id, legal_name FROM companies WHERE is_ankara = TRUE")).fetchall()
db_names = {name: cid for cid, name in rows}

vals = []
for rec in aso:
    unvan = rec.get("unvan", "").strip()
    cid = db_names.get(unvan)
    if not cid:
        continue
    adres = (rec.get("adres") or "").strip()
    if adres:
        vals.append((cid, adres[:500]))

print("bulk adres to update:", len(vals))
batch = 50
for i in range(0, len(vals), batch):
    chunk = vals[i:i+batch]
    sql = "UPDATE companies c SET adres = v.adres, updated_at = NOW() FROM (VALUES " + ", ".join([\"(:cid" + str(j) + ", :adres" + str(j) + ")\" for j in range(len(chunk))]) + ") AS v(cid, adres) WHERE c.company_id = v.cid AND (c.adres IS NULL OR c.adres = :empty)"
    params = {}
    for j, (cid, adres) in enumerate(chunk):
        params["cid" + str(j)] = cid
        params["adres" + str(j)] = adres
    params["empty"] = ""
    result = conn.execute(text(sql), params)
    print("batch " + str(i // batch + 1) + ": updated " + str(result.rowcount))
conn.commit()
print("done")
