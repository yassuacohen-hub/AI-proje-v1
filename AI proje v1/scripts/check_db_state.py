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
            COUNT(*) FILTER(WHERE c.tax_number IS NOT NULL AND c.tax_number != '') as tax_no,
            COUNT(*) FILTER(WHERE c.vergi_no IS NOT NULL AND c.vergi_no != '') as vergi_no,
            COUNT(*) FILTER(WHERE COALESCE(c.tax_number, c.vergi_no) IS NOT NULL AND COALESCE(c.tax_number, c.vergi_no) != '') as vkn_either,
            COUNT(*) FILTER(WHERE c.website_domain IS NOT NULL AND c.website_domain != '') as web,
            COUNT(*) FILTER(WHERE c.osb_parsel IS NOT NULL AND c.osb_parsel != '') as parsel,
            COUNT(*) FILTER(WHERE sr.raw_payload ? 'adres' AND NULLIF(sr.raw_payload->>'adres', '') IS NOT NULL) as adres,
            COUNT(*) FILTER(WHERE c.primary_phone IS NOT NULL AND c.primary_phone != '') as tel,
            COUNT(*) FILTER(WHERE c.primary_email IS NOT NULL AND c.primary_email != '') as email,
            COUNT(*) FILTER(WHERE c.nace_code IS NOT NULL AND c.nace_code != '') as nace,
            AVG(c.data_quality_score) as avg_score
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
    """)).mappings().first()
    print("Total:", r["total"])
    print("tax_number:", r["tax_no"])
    print("vergi_no:", r["vergi_no"])
    print("VKN (either):", r["vkn_either"])
    print("web:", r["web"])
    print("parsel:", r["parsel"])
    print("adres:", r["adres"])
    print("tel:", r["tel"])
    print("email:", r["email"])
    print("nace:", r["nace"])
    print("avg_score:", round(r["avg_score"], 2))
