#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text
import json

eng = get_engine()
with eng.connect() as conn:
    # Check how many have emailler in raw_payload
    r = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM source_records
        WHERE raw_payload->>'emailler' IS NOT NULL
        AND raw_payload->>'emailler' != ''
    """)).scalar()
    print(f"emailler raw_payload ta var: {r}")
    
    # Check how many have telefonlar in raw_payload
    r2 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM source_records
        WHERE raw_payload->>'telefonlar' IS NOT NULL
        AND raw_payload->>'telefonlar' != ''
    """)).scalar()
    print(f"telefonlar raw_payload ta var: {r2}")
    
    # Check a sample raw_payload
    r3 = conn.execute(text("""
        SELECT sr.raw_payload FROM source_records sr
        LEFT JOIN companies c ON c.source_record_id = sr.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        LIMIT 3
    """)).fetchall()
    for i, row in enumerate(r3):
        payload = row[0]
        if payload and isinstance(payload, dict):
            print(f"\nSample {i+1} keys: {list(payload.keys())[:15]}")
            if "emailler" in payload:
                print(f"  emailler: {payload['emailler']}")
            if "telefonlar" in payload:
                print(f"  telefonlar: {payload['telefonlar']}")
