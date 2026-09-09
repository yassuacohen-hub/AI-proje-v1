#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug emailler field in raw_payload."""
import sys, json
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    rows = conn.execute(text("""
        SELECT sr.raw_payload->>'emailler' as emailler
        FROM source_records sr
        LEFT JOIN companies c ON c.source_record_id = sr.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND (c.primary_email IS NULL OR c.primary_email = '')
        AND sr.raw_payload->>'emailler' IS NOT NULL
        LIMIT 10
    """)).fetchall()
    
    for i, row in enumerate(rows):
        val = row[0]
        print(f"Record {i+1}: {val[:200]}")
