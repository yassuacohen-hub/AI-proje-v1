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
        SELECT sr.raw_payload FROM source_records sr
        LEFT JOIN companies c ON c.source_record_id = sr.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        LIMIT 10
    """)).fetchall()
    
    for i, row in enumerate(rows):
        payload = row[0]
        if isinstance(payload, dict):
            print(f"\nFirma {i+1}:")
            for key in ['web_sitesi', 'adres', 'sektor', 'vergi_no', 'nace_code', 'osb_parsel', 'telefonlar', 'emailler']:
                val = payload.get(key)
                if val is not None:
                    print(f"  {key}: {str(val)[:80]}")
