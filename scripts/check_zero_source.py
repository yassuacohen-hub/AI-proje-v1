#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    # Check source of zero-score companies
    r = conn.execute(text("""
        SELECT sr.source_id, COUNT(*) as cnt
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        GROUP BY sr.source_id
        ORDER BY cnt DESC
    """)).fetchall()
    
    print("Zero-score companies by source:")
    for row in r:
        print(f"  source_id={row[0]}: {row[1]}")
