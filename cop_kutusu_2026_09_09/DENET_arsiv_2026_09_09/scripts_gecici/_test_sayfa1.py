import json, sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
conn = engine.connect()

# Build DB name index
rows = conn.execute(text("SELECT legal_name, company_id FROM companies WHERE is_ankara = TRUE")).fetchall()
db_index = {}
for name, cid in rows:
    db_index[name.strip()] = cid
print("DB index size:", len(db_index))

def try_update(cid, adres, web):
    updates = {}
    params = {"cid": cid}
    if adres:
        updates["adres = :adres"] = True
        params["adres"] = adres[:500]
    if web:
        updates["website_domain = :web"] = True
        params["web"] = web.lower().strip()
    if updates:
        sql = "UPDATE companies SET " + ", ".join(updates.keys()) + ", updated_at = NOW() WHERE company_id = :cid"
        conn.execute(text(sql), params)
        return True
    return False

stats = {"adres": 0, "web": 0, "vergi": 0, "matched": 0}

# Process firmalar_sayfa1.jsonl (has vergi_no)
f1 = "data/ostim/firmalar_sayfa1.jsonl"
if os.path.exists(f1):
    lines = open(f1, "r", encoding="utf-8").read().splitlines()
    recs = [json.loads(l) for l in lines if l.strip()]
    for r in recs:
        unvan = (r.get("unvan") or "").strip()
        vergi = (r.get("vergi_no") or "").strip()
        adres = (r.get("adres") or "").strip()
        web = (r.get("web_sitesi") or "").strip()
        if not unvan:
            continue
        cid = db_index.get(unvan)
        if not cid:
            continue
        stats["matched"] += 1
        if try_update(cid, adres, web):
            pass
        if vergi:
            r2 = conn.execute(text("UPDATE companies SET tax_number = COALESCE(:v, tax_number), vergi_no = COALESCE(:v, vergi_no) WHERE company_id = :cid"), {"v": vergi, "cid": cid})
            stats["vergi"] += r2.rowcount

conn.commit()
print("firmalar_sayfa1 stats:", stats)
conn.close()
