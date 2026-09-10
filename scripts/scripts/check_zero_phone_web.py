#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    # Check if zero-score companies with phone have web in raw_payload
    r = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        AND (c.primary_phone IS NOT NULL AND c.primary_phone != '')
        AND sr.raw_payload->>'web_sitesi' IS NOT NULL
        AND sr.raw_payload->>'web_sitesi' != ''
    """)).scalar()
    print(f"Score 0, phone var, raw_payload web_sitesi var: {r}")
    
    # Check if they have adres in raw_payload
    r2 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        AND (c.primary_phone IS NOT NULL AND c.primary_phone != '')
        AND sr.raw_payload->>'adres' IS NOT NULL
        AND sr.raw_payload->>'adres' != ''
    """)).scalar()
    print(f"Score 0, phone var, raw_payload adres var: {r2}")
    
    # Check if they have vergi_no in raw_payload
    r3 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        AND (c.primary_phone IS NOT NULL AND c.primary_phone != '')
        AND sr.raw_payload->>'vergi_no' IS NOT NULL
        AND sr.raw_payload->>'vergi_no' != ''
    """)).scalar()
    print(f"Score 0, phone var, raw_payload vergi_no var: {r3}")
