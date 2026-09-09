import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
with engine.connect() as conn:
    lines = open("data/ostim/firmalar_detayli.jsonl", "r", encoding="utf-8").read().splitlines()
    recs = [json.loads(l) for l in lines if l.strip()]
    pairs = []
    for r in recs:
        unvan = (r.get("unvan") or "").strip()
        web = (r.get("web_sitesi") or "").strip()
        adres = (r.get("adres") or "").strip()
        if not unvan or (not web and not adres):
            continue
        pairs.append((unvan, web, adres))
    print("pairs:", len(pairs))
    rows = conn.execute(text("SELECT legal_name FROM companies WHERE is_ankara = TRUE")).fetchall()
    db_names = {r[0] for r in rows}
    exact = sum(1 for u, w, a in pairs if u in db_names)
    print("exact matches:", exact)
