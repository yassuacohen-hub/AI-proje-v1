#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""NACE eksiklerini ASO verisi ile doldur."""
import json, sys
from pathlib import Path
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.db.connection import get_engine

ASO_PATH = ROOT / "data" / "aso" / "aso_full.jsonl"
engine = get_engine()

# Load ASO data
records = []
with open(ASO_PATH, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except:
                pass

print(f"ASO kaydı: {len(records)}")

# Build lookup by cleaned company name
aso_lookup = {}
for rec in records:
    raw_unvan = (rec.get("unvan") or "").strip()
    prefix = "(İFLAS NEDENİYLE) TASFİYE HALİNDE "
    unvan = raw_unvan[len(prefix):].strip() if raw_unvan.startswith(prefix) else raw_unvan
    nace = rec.get("naceKod")
    if nace:
        aso_lookup[unvan.lower()] = nace

print(f"ASO NACE lookup: {len(aso_lookup)} firma")

with engine.connect() as conn:
    # Find companies with missing NACE
    rows = conn.execute(text("""
        SELECT c.company_id, c.legal_name, c.nace_code
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND (c.nace_code IS NULL OR c.nace_code = '')
    """)).fetchall()
    
    print(f"NACE eksik firma: {len(rows)}")
    
    updated = 0
    for row in rows:
        company_id, legal_name, current_nace = row
        key = (legal_name or "").lower().strip()
        
        if key in aso_lookup:
            nace = aso_lookup[key]
            conn.execute(text("""
                UPDATE companies SET nace_code = :nace
                WHERE company_id = :cid
            """), {"nace": nace, "cid": company_id})
            updated += 1
    
    conn.commit()
    print(f"NACE doldurulan firma: {updated}")
