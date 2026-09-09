#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    rows = conn.execute(text("""
        SELECT sr.raw_payload FROM source_records sr
        LEFT JOIN companies c ON c.source_record_id = sr.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        AND (c.primary_phone IS NOT NULL AND c.primary_phone != '')
        LIMIT 5
    """)).fetchall()
    
    for i, row in enumerate(rows):
        payload = row[0]
        print(f"\nFirma {i+1}:")
        if isinstance(payload, dict):
            for key, val in payload.items():
                if val is not None and val != '' and val != []:
                    print(f"  {key}: {str(val)[:100]}")
