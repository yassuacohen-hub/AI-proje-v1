import json, os
from pathlib import Path

files = [
    "data/ostim/firmalar_vkn_ekli.jsonl",
    "data/ostim/firmalar_sayfa1.jsonl",
    "data/ostim/firmalar_full.jsonl",
    "data/ostim/firmalar_detayli.jsonl",
    "data/ostim/firmalar_detailed.jsonl",
    "data/ostim/firmalar_vkn_ekli.jsonl",
    "data/orchestrator/merged_companies.jsonl",
    "data/baskent/firmalar.jsonl",
    "data/ivedik/firmalar_detayli.jsonl",
    "data/ivedik/firmalar.jsonl",
    "data/aso/aso_full.jsonl",
]

for f in files:
    if not os.path.exists(f):
        print(f, ": NOT FOUND")
        continue
    lines = open(f, "r", encoding="utf-8").read().splitlines()
    recs = [json.loads(l) for l in lines if l.strip()]
    web = sum(1 for r in recs if r.get("web_sitesi"))
    adres = sum(1 for r in recs if r.get("adres"))
    vergi = sum(1 for r in recs if r.get("vergi_no") or r.get("tax_number"))
    print(f, ": total=", len(recs), "web=", web, "adres=", adres, "vergi=", vergi)
