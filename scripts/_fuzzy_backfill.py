import json, sys, os
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sqlalchemy import text
from company_master.db.connection import get_engine

PROJE_KOK = Path(__file__).resolve().parents[1]
engine = get_engine()
conn = engine.connect()

files = [
    "data/ostim/firmalar_vkn_ekli.jsonl",
    "data/ostim/firmalar_detayli.jsonl",
    "data/ostim/firmalar_detailed.jsonl",
    "data/baskent/firmalar.jsonl",
    "data/aso/aso_full.jsonl",
]

rows = conn.execute(text("SELECT legal_name, company_id FROM companies WHERE is_ankara = TRUE")).fetchall()
db_names = {r[0].strip() for r in rows}

unmatched = []
for f in files:
    if not os.path.exists(f):
        continue
    lines = open(f, "r", encoding="utf-8").read().splitlines()
    recs = [json.loads(l) for l in lines if l.strip()]
    for r in recs:
        unvan = (r.get("unvan") or "").strip()
        web = (r.get("web_sitesi") or "").strip()
        adres = (r.get("adres") or "").strip()
        vergi = (r.get("vergi_no") or "").strip()
        if not unvan or unvan in db_names or (not web and not adres and not vergi):
            continue
        unmatched.append((unvan, web, adres, vergi))

print("unmatched records:", len(unmatched))

conn.execute(text("DROP TABLE IF EXISTS tmp_ostim"))
conn.execute(text("CREATE TEMP TABLE tmp_ostim (unvan TEXT, web TEXT, adres TEXT, vergi TEXT)"))

batch = 500
for i in range(0, len(unmatched), batch):
    chunk = unmatched[i:i+batch]
    vals = []
    params = {}
    for j, (unvan, web, adres, vergi) in enumerate(chunk):
        vals.append(f"(:u{j}, :w{j}, :a{j}, :v{j})")
        params[f"u{j}"] = unvan
        params[f"w{j}"] = web
        params[f"a{j}"] = adres[:500] if adres else None
        params[f"v{j}"] = vergi if vergi else None
    sql = "INSERT INTO tmp_ostim (unvan, web, adres, vergi) VALUES " + ", ".join(vals)
    conn.execute(text(sql), params)

conn.commit()

# Lateral join for efficient best-match lookup
matched = conn.execute(text("""
    SELECT t.unvan, c.company_id, t.web, t.adres, t.vergi, c.sim
    FROM tmp_ostim t
    LEFT JOIN LATERAL (
        SELECT company_id, legal_name, similarity(t.unvan, legal_name) as sim
        FROM companies
        WHERE is_ankara = TRUE AND t.unvan % legal_name
        ORDER BY similarity(t.unvan, legal_name) DESC
        LIMIT 1
    ) c ON true
    WHERE c.sim > 0.5
""")).fetchall()

print("fuzzy matches (>0.5):", len(matched))
for unvan, cid, web, adres, vergi, sim in matched[:10]:
    print(f"  {sim:.2f}: {unvan}")

stats = {"web": 0, "adres": 0, "vergi": 0}
for unvan, cid, web, adres, vergi, sim in matched:
    updates = {}
    params = {"cid": cid}
    if web:
        updates["website_domain = :web"] = True
        params["web"] = web.lower().strip()
        stats["web"] += 1
    if adres:
        updates["adres = :adres"] = True
        params["adres"] = adres[:500]
        stats["adres"] += 1
    if vergi:
        updates["tax_number = :tax, vergi_no = :tax2"] = True
        params["tax"] = vergi
        params["tax2"] = vergi
        stats["vergi"] += 1
    if updates:
        sql = "UPDATE companies SET " + ", ".join(updates.keys()) + ", updated_at = NOW() WHERE company_id = :cid"
        conn.execute(text(sql), params)

conn.commit()
print("fuzzy backfill stats:", stats)
conn.close()
