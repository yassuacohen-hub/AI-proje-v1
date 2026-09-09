#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    # Companies with website but no VKN
    r = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND (c.website_domain IS NOT NULL AND c.website_domain != '')
        AND COALESCE(c.tax_number, c.vergi_no) IS NULL
    """)).scalar()
    print(f'Websitesi var ama VKN yok: {r}')
    
    # Companies with no address but have other data
    r2 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND (sr.raw_payload->>'adres' IS NULL OR sr.raw_payload->>'adres' = '')
        AND (c.primary_phone IS NOT NULL OR c.primary_email IS NOT NULL OR c.website_domain IS NOT NULL)
    """)).scalar()
    print(f'Adres yok ama diger veri var: {r2}')
    
    # Companies with no phone but have other data
    r3 = conn.execute(text("""
        SELECT COUNT(*) as cnt FROM companies c
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND (c.primary_phone IS NULL OR c.primary_phone = '')
        AND (c.website_domain IS NOT NULL OR c.primary_email IS NOT NULL OR c.vergi_no IS NOT NULL)
    """)).scalar()
    print(f'Telefon yok ama diger veri var: {r3}')
