#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    # Check companies with score 0
    rows = conn.execute(text("""
        SELECT c.company_id, c.legal_name, c.data_quality_score,
               c.primary_phone, c.primary_email, c.website_domain,
               c.tax_number, c.vergi_no, c.nace_code, c.osb_parsel
        FROM companies c
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.data_quality_score = 0
        LIMIT 5
    """)).fetchall()
    
    print("Score 0 olan firmalar:")
    for row in rows:
        print(f"  {row[1][:50]}: phone={row[3]}, email={row[4]}, web={row[5]}, tax={row[6]}, vergi={row[7]}, nace={row[8]}, parsel={row[9]}")
