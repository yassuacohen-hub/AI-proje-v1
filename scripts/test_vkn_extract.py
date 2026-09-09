#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test footer VKN extractor on one website."""
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text
import requests
import re

eng = get_engine()
with eng.connect() as conn:
    # Get one company with website but no VKN
    row = conn.execute(text("""
        SELECT c.company_id, c.legal_name, c.website_domain
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.website_domain IS NOT NULL AND c.website_domain != ''
        AND COALESCE(c.tax_number, c.vergi_no) IS NULL
        LIMIT 5
    """)).fetchall()
    
    for r in row:
        print(f"Firma: {r[1]}")
        print(f"Website: {r[2]}")
        try:
            resp = requests.get(r[2], timeout=10, verify=False)
            if resp.status_code == 200:
                html = resp.text
                # Look for VKN pattern
                vkn_pattern = re.compile(r'\b(\d{10,11})\b')
                matches = vkn_pattern.findall(html)
                print(f"  Bulunan sayilar: {matches[:10]}")
                # Look for VKN keywords
                vkn_keywords = ['vergi no', 'vkn', 'vergi dairesi']
                for kw in vkn_keywords:
                    if kw in html.lower():
                        idx = html.lower().find(kw)
                        context = html[max(0, idx-50):idx+100]
                        print(f"  '{kw}' context: {context[:100]}")
                        break
            else:
                print(f"  HTTP {resp.status_code}")
        except Exception as e:
            print(f"  Hata: {e}")
        print()
