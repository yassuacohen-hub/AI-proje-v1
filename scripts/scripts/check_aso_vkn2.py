#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    # Check VKN length distribution after ASO ingest
    rows = conn.execute(text("""
        SELECT LENGTH(vergi_no) as len, COUNT(*) as cnt
        FROM companies
        WHERE vergi_no IS NOT NULL AND vergi_no != ''
        GROUP BY LENGTH(vergi_no)
        ORDER BY len
    """)).fetchall()
    print('VKN uzunluk dagilimi (ASO ingest sonrasi):')
    total = 0
    for row in rows:
        print(f'  {row[0]} karakter: {row[1]} firma')
        total += row[1]
    print(f'Toplam: {total}')
    
    # Check if ASO source has VKN data
    rows2 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE sr.raw_payload @> '{"kaynak": "aso.org.tr"}'::jsonb
        AND COALESCE(c.tax_number, c.vergi_no) IS NOT NULL
    """)).scalar()
    print(f'\nASO kaynakli VKN: {rows2}')
    
    # Check how many have ticaretSicilNo in raw_payload
    rows3 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM source_records
        WHERE raw_payload->>'ticaretSicilNo' IS NOT NULL
        AND raw_payload->>'ticaretSicilNo' != ''
    """)).scalar()
    print(f'ticaretSicilNo kaydi: {rows3}')
