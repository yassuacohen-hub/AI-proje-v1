#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    r = conn.execute(text("""
        SELECT COUNT(*) as total,
            COUNT(*) FILTER(WHERE source_id = (SELECT source_id FROM sources WHERE source_name = 'aso.org.tr' LIMIT 1)) as aso_records
        FROM source_records
    """)).mappings().first()
    print("source_records total:", r["total"])
    print("ASO source_records:", r["aso_records"])

    r2 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE sr.raw_payload @> '{"kaynak": "aso.org.tr"}'::jsonb
    """)).mappings().first()
    print("Companies with ASO payload:", r2["cnt"])
