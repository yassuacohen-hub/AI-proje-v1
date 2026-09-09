# -*- coding: utf-8 -*-
"""Gecici: pano guncelleme (Y15 done, Y20 acilis)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")

PANO = Path("data/orchestrator/task_board.json")
gs = json.load(open(PANO, encoding="utf-8"))

for g in gs:
    if g.get("id") == "Y15":
        g["durum"] = "done"
        g["not"] = (
            "TAMAMLANDI 2026-09-09: scripts/setup_local_indexes.py - pg_trgm extension + "
            "7 index (legal_name_trgm, search_text_trgm, er_company_id, sr_source_id, "
            "sr_external_id, nace, score). ILIKE arama 11.6ms -> 1.4ms (~8x ek hizlanma, "
            "Supabase'e gore ~600x). EXPLAIN OK. "
            "Not: Supabase ile testler 25 passed (dogrulandi)."
        )
        print("Y15 -> done")
    if g.get("id") == "Y20":
        g["durum"] = "plan"
        print("Y20 zaten var")
else:
    pass

mevcut_id = [g.get("id") for g in gs]
if "Y20" not in mevcut_id:
    gs.append({
        "id": "Y20",
        "baslik": "BUG: connection.py DATABASE_URL env override testlerde sqlite'a dusuyor",
        "sahip": "gelistirici",
        "durum": "plan",
        "not": (
            "DATABASE_URL=postgresql+psycopg://... env var'i set edilip testler kosuldugunda "
            "web_app sqlite fallback'a geciyor (no such table: companies, 19 fail). "
            "get_database_url()/get_engine() +psycopg sonekli URL'leri veya env onceligini "
            "duzgun islemeli; testlerin yerel PG ile de kosmasi gerekir (Y15 index dogrulamasi "
            "yerelde manuel yapildi)."
        ),
    })
    print("Y20 eklendi")

json.dump(gs, open(PANO, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("PANO KAYDEDILDI")
