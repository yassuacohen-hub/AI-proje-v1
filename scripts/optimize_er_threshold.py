#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Entity resolution threshold optimization with rapidfuzz."""
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text
from rapidfuzz import fuzz

eng = get_engine()
with eng.connect() as conn:
    # Get sample data for threshold testing
    rows = conn.execute(text("""
        SELECT sr.raw_name, c.legal_name 
        FROM source_records sr
        LEFT JOIN companies c ON c.source_record_id = sr.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        LIMIT 100
    """)).fetchall()
    
    print("Threshold optimization testi:")
    print(f"Test edilen cift sayisi: {len(rows)}")
    
    # Test different thresholds
    for threshold in [0.7, 0.75, 0.8, 0.85, 0.9]:
        matches = 0
        for row in rows:
            raw_name = row[0] or ""
            legal_name = row[1] or ""
            if raw_name and legal_name:
                score = fuzz.ratio(raw_name.lower(), legal_name.lower()) / 100
                if score >= threshold:
                    matches += 1
        
        print(f"  Threshold {threshold}: {matches} eslesme ({matches/len(rows)*100:.1f}%)")
