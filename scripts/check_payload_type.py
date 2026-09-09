#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    rows = conn.execute(text("""
        SELECT sr.raw_payload FROM source_records sr
        LEFT JOIN companies c ON c.source_record_id = sr.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND (c.primary_email IS NULL OR c.primary_email = '')
        LIMIT 3
    """)).fetchall()
    
    for i, row in enumerate(rows):
        payload = row[0]
        print(f"Record {i+1}: type={type(payload)}")
        if isinstance(payload, dict):
            print(f"  keys: {list(payload.keys())[:10]}")
            if "emailler" in payload:
                print(f"  emailler: {payload['emailler']}")
        elif isinstance(payload, str):
            print(f"  value: {payload[:100]}")
        else:
            print(f"  value: {payload}")
