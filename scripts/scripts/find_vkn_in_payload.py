#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text
import re

eng = get_engine()
VKN_PATTERN = re.compile(r'\b(\d{10,11})\b')

with eng.connect() as conn:
    # Find VKNs in raw_payload for zero-score companies
    rows = conn.execute(text("""
        SELECT sr.raw_payload FROM source_records sr
        LEFT JOIN companies c ON c.source_record_id = sr.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        AND (c.primary_phone IS NOT NULL AND c.primary_phone != '')
        LIMIT 100
    """)).fetchall()
    
    found = 0
    for row in rows:
        payload = row[0]
        if isinstance(payload, dict):
            # Check all string values for VKN patterns
            for key, val in payload.items():
                if isinstance(val, str) and val:
                    matches = VKN_PATTERN.findall(val)
                    if matches:
                        found += len(matches)
                        print(f"Found VKN in {key}: {matches}")
    
    print(f"\nTotal VKN patterns found: {found}")
