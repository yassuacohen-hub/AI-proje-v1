#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    # Check zero-score companies data coverage
    r = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        AND (c.primary_phone IS NOT NULL AND c.primary_phone != '')
    """)).scalar()
    print(f"Score 0 ama telefon olan: {r}")
    
    r2 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        AND (c.primary_email IS NOT NULL AND c.primary_email != '')
    """)).scalar()
    print(f"Score 0 ama email olan: {r2}")
    
    r3 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        AND c.website_domain IS NOT NULL AND c.website_domain != ''
    """)).scalar()
    print(f"Score 0 ama web olan: {r3}")
    
    r4 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        AND sr.raw_payload->>'adres' IS NOT NULL
        AND sr.raw_payload->>'adres' != ''
    """)).scalar()
    print(f"Score 0 ama adres olan: {r4}")
