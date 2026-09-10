#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    rows = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
    """)).scalar()
    print(f"Score 0 olan firma: {rows}")
    
    rows2 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        AND sr.raw_payload IS NOT NULL
    """)).scalar()
    print(f"Score 0 ama raw_payload olan: {rows2}")
    
    rows3 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        AND sr.raw_payload->>'web_sitesi' IS NOT NULL
        AND sr.raw_payload->>'web_sitesi' != ''
    """)).scalar()
    print(f"Score 0 ama web_sitesi olan: {rows3}")
