#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    # Companies with no vergi_no AND no address
    r = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND COALESCE(c.tax_number, c.vergi_no) IS NULL
        AND (sr.raw_payload->>'adres' IS NULL OR sr.raw_payload->>'adres' = '')
    """)).scalar()
    print(f'VKN yok ve adres yok: {r}')
    
    # Companies with no vergi_no AND no website
    r2 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND COALESCE(c.tax_number, c.vergi_no) IS NULL
        AND (c.website_domain IS NULL OR c.website_domain = '')
    """)).scalar()
    print(f'VKN yok ve web yok: {r2}')
    
    # Companies with all three missing (phone+email+VKN)
    r3 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND (COALESCE(c.primary_phone, sr.raw_phone) IS NULL OR COALESCE(c.primary_phone, sr.raw_phone) = '')
        AND (COALESCE(c.primary_email, sr.raw_email) IS NULL OR COALESCE(c.primary_email, sr.raw_email) = '')
        AND (COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '')
    """)).scalar()
    print(f'Phone+email+VKN hepsi yok: {r3}')
    
    # Distribution of quality scores
    r4 = conn.execute(text("""
        SELECT 
            COUNT(*) FILTER (WHERE data_quality_score = 0) as zero,
            COUNT(*) FILTER (WHERE data_quality_score > 0 AND data_quality_score < 20) as low,
            COUNT(*) FILTER (WHERE data_quality_score >= 20 AND data_quality_score < 40) as mid,
            COUNT(*) FILTER (WHERE data_quality_score >= 40 AND data_quality_score < 60) as good,
            COUNT(*) FILTER (WHERE data_quality_score >= 60 AND data_quality_score < 80) as better,
            COUNT(*) FILTER (WHERE data_quality_score >= 80) as best
        FROM companies
        WHERE is_ankara=TRUE AND is_osb_member=TRUE
    """)).mappings().first()
    print(f'\nKalite skoru dagilimi:')
    print(f'  0: {r4["zero"]}')
    print(f'  1-19: {r4["low"]}')
    print(f'  20-39: {r4["mid"]}')
    print(f'  40-59: {r4["good"]}')
    print(f'  60-79: {r4["better"]}')
    print(f'  80+: {r4["best"]}')
