#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text
import json

eng = get_engine()
with eng.connect() as conn:
    rows = conn.execute(text("""
        SELECT sr.raw_payload, c.data_quality_score, c.legal_name
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        LIMIT 5
    """)).fetchall()
    
    for i, row in enumerate(rows):
        payload = row[0]
        score = row[1]
        name = row[2]
        print(f"Firma {i+1}: {name[:50]} (score={score})")
        if payload and isinstance(payload, dict):
            print(f"  Keys: {list(payload.keys())[:10]}")
            if "adres" in payload:
                print(f"  adres: {str(payload['adres'])[:80]}")
            if "vergi_no_extracted" in payload:
                print(f"  vergi_no_extracted: {payload['vergi_no_extracted']}")
        else:
            print("  raw_payload: NULL/empty")
        print()
