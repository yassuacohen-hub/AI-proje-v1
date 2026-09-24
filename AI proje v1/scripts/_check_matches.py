import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
conn = engine.connect()
rows = conn.execute(text("SELECT legal_name FROM companies WHERE is_ankara = TRUE")).fetchall()
db_names = {r[0].strip() for r in rows}
print("DB names:", len(db_names))

files = [
    "data/ostim/firmalar_vkn_ekli.jsonl",
    "data/ostim/firmalar_detayli.jsonl",
    "data/ostim/firmalar_detailed.jsonl",
    "data/baskent/firmalar.jsonl",
    "data/aso/aso_full.jsonl",
    "data/orchestrator/merged_companies.jsonl",
]

for f in files:
    lines = open(f, "r", encoding="utf-8").read().splitlines()
    recs = [json.loads(l) for l in lines if l.strip()]
    names = [r.get("unvan", "").strip() for r in recs if r.get("unvan")]
    exact = sum(1 for n in names if n in db_names)
    print(f, ": total=", len(recs), "exact_matches=", exact)
conn.close()
