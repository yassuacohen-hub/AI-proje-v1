#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""NACE eksiklerini raw_payload'daki sektor field'indan doldur."""
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text
import re

eng = get_engine()
with eng.connect() as conn:
    # Find companies with missing NACE but have sektor in raw_payload
    rows = conn.execute(text("""
        SELECT c.company_id, sr.raw_payload->>'sektor' as sektor
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND (c.nace_code IS NULL OR c.nace_code = '')
        AND sr.raw_payload->>'sektor' IS NOT NULL
        AND sr.raw_payload->>'sektor' != ''
    """)).fetchall()
    
    print(f"NACE eksik ama sektor olan: {len(rows)}")
    
    updated = 0
    for row in rows:
        company_id, sektor = row
        if not sektor:
            continue
        
        # Extract numeric code from end
        m = re.search(r'(\d+)$', sektor.strip())
        if m:
            nace_code = m.group(1)
            # Convert to standard NACE format if possible
            # e.g., "757" -> "43.21.01" (this is just a placeholder)
            # For now, use the raw number as fallback
            conn.execute(text("""
                UPDATE companies SET nace_code = :nace
                WHERE company_id = :cid
            """), {"nace": nace_code, "cid": company_id})
            updated += 1
    
    conn.commit()
    print(f"NACE doldurulan firma: {updated}")
