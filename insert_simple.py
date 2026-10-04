#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VERI-NACE-COKLU-01: Simple insert with verbose output"""

import sys
sys.path.insert(0, 'src')

import re
from collections import defaultdict
from company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()

def normalize_nace(code: str) -> str:
    if not code: return ""
    code = str(code).strip()
    match = re.match(r'^(\d{2}\.\d{2}(?:\.\d{2})?)', code)
    return match.group(1) if match else ""

def parse_raw_nace(raw_nace: str) -> list[str]:
    if not raw_nace: return []
    parts = re.split(r'[,;/\|\s]+', raw_nace.strip())
    return [normalize_nace(p) for p in parts if normalize_nace(p)]

# Quick setup
with engine.connect() as conn:
    r = conn.execute(text("SELECT nace_code FROM nace_codes"))
    valid_codes = {row[0] for row in r}
    r = conn.execute(text("SELECT source_id, source_name FROM sources"))
    source_map = {row[1]: str(row[0]) for row in r}

default_source = source_map.get("ostim.org.tr")

with engine.connect() as conn:
    r = conn.execute(text('''
        SELECT sr.company_id, sr.raw_nace, sr.source_id
        FROM source_records sr
        WHERE sr.company_id IS NOT NULL 
        AND sr.raw_nace IS NOT NULL 
        AND sr.raw_nace != ''
        AND sr.raw_nace ~ '^[0-9]+\\.[0-9]+'
    '''))
    records = r.fetchall()

print(f"Records: {len(records)}")

company_nace = defaultdict(lambda: {"codes": set(), "source_id": None})
for company_id, raw_nace, src_id in records:
    for code in parse_raw_nace(raw_nace):
        if code in valid_codes:
            company_nace[str(company_id)]["codes"].add(code)
            if src_id: company_nace[str(company_id)]["source_id"] = str(src_id)

print(f"Companies: {len(company_nace)}")

batch_data = []
primary_set = set()
default_source = source_map.get("ostim.org.tr")

for cid, data in company_nace.items():
    codes = sorted(data["codes"])
    src = data["source_id"] or source_map.get("ostim.org.tr")
    for i, code in enumerate(codes):
        batch_data.append({
            "company_id": cid, "nace_code": code, "nace_version": "2026.01.01",
            "nace_level": code.count('.') + 1, "is_primary": i==0,
            "source_id": src or default_source, "confidence": 0.9, "verified_at": None
        })
        if i==0: primary_set.add(cid)

print(f"Batch size: {len(batch_data)}, Primary: {len(primary_set)}")

# Do it in small batches
with engine.begin() as conn:
    print("DELETE...")
    conn.execute(text("DELETE FROM company_industries"))
    print("DELETE done")
    
    batch_size = 500
    for i in range(0, len(batch_data), batch_size):
        batch = batch_data[i:i+batch_size]
        conn.execute(text('''
            INSERT INTO company_industries 
            (company_id, nace_code, nace_version, nace_level, is_primary, source_id, confidence, verified_at)
            VALUES (:company_id, :nace_code, :nace_version, :nace_level, :is_primary, :source_id, :confidence, :verified_at)
        '''), batch)
        print(f"  Inserted batch {i//batch_size + 1}: {len(batch)} rows")
    
    print("All inserts done")
    
    # Update companies
    for cid in primary_set:
        main_code = min(company_nace[cid]["codes"])
        conn.execute(text('UPDATE companies SET nace_code = :c WHERE company_id = :cid'), {"c": min(company_nace[cid]["codes"]), "cid": cid})
    
    print("Updates done")

print("COMMIT")
print("ALL DONE")