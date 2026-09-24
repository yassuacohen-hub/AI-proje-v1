import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
conn = engine.connect()
rows = conn.execute(text("SELECT legal_name, website_domain, web_sitesi, adres, tax_number, vergi_no FROM companies WHERE is_ankara = TRUE")).fetchall()
db = {}
for name, web_dom, web_site, adres, tax, vergi in rows:
    db[name.strip()] = {
        "web": bool(web_dom or web_site),
        "adres": bool(adres),
        "tax": bool(tax or vergi),
    }

files = [
    ("data/ostim/firmalar_vkn_ekli.jsonl", ["web_sitesi", "adres"]),
    ("data/ostim/firmalar_detayli.jsonl", ["web_sitesi", "adres"]),
    ("data/ostim/firmalar_detailed.jsonl", ["web_sitesi", "adres"]),
    ("data/baskent/firmalar.jsonl", ["web_sitesi", "adres"]),
    ("data/aso/aso_full.jsonl", ["adres"]),
    ("data/orchestrator/merged_companies.jsonl", ["web_sitesi", "adres"]),
]

best = {}
for f, fields in files:
    lines = open(f, "r", encoding="utf-8").read().splitlines()
    recs = [json.loads(l) for l in lines if l.strip()]
    updates = {"web": 0, "adres": 0}
    for r in recs:
        unvan = (r.get("unvan") or "").strip()
        if not unvan or unvan not in db:
            continue
        cur = db[unvan]
        web = (r.get("web_sitesi") or "").strip()
        adres = (r.get("adres") or "").strip()
        if "web_sitesi" in fields and web and not cur["web"]:
            updates["web"] += 1
            cur["web"] = True
        if "adres" in fields and adres and not cur["adres"]:
            updates["adres"] += 1
            cur["adres"] = True
    print(f, updates)
conn.close()
