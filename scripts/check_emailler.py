#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    rows = conn.execute(text("""
        SELECT raw_payload->>'emailler' as emailler
        FROM source_records
        WHERE raw_payload->>'emailler' IS NOT NULL
        AND raw_payload->>'emailler' != ''
    """)).fetchall()
    
    non_empty = 0
    empty = 0
    for row in rows:
        val = row[0]
        try:
            parsed = json.loads(val)
            if parsed and len(parsed) > 0:
                non_empty += 1
            else:
                empty += 1
        except:
            empty += 1
    
    print(f"emailler dolu liste: {non_empty}")
    print(f"emailler bos liste: {empty}")
