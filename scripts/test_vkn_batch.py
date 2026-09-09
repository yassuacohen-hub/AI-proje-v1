#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Footer VKN extractor - 100 firma ile test."""
import re, json, sys, time, requests
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine
from sqlalchemy import text

VKN_PATTERN = re.compile(r'\b(\d{10,11})\b')
VKN_KEYWORDS = ['vergi no', 'vkn', 'vergi dairesi', 'tax number', 'tax id']

def is_valid_candidate(candidate, context=''):
    if len(candidate) not in (10, 11):
        return False
    if candidate[0] == '0':
        return False
    ctx = context.lower()
    for kw in VKN_KEYWORDS:
        if kw in ctx:
            return True
    if len(candidate) == 11 and all(c.isdigit() for c in candidate):
        return True
    return False

def extract_from_html(html):
    candidates = []
    for m in VKN_PATTERN.finditer(html):
        v = m.group(1)
        s = max(0, m.start() - 200)
        e = min(len(html), m.end() + 200)
        if is_valid_candidate(v, html[s:e]):
            candidates.append(v)
    return list(set(candidates))

def fetch_website(url, timeout=10):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=timeout, verify=False)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None

engine = get_engine()
with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT c.company_id, c.legal_name, c.website_domain
        FROM companies c
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND c.website_domain IS NOT NULL AND c.website_domain != ''
        AND COALESCE(c.tax_number, c.vergi_no) IS NULL
        LIMIT 100
    """)).fetchall()

print(f"Test edilecek firma sayisi: {len(rows)}")
found = 0
errors = 0

for i, row in enumerate(rows):
    company_id, name, website = row
    if not website.startswith(('http://', 'https://')):
        website = 'https://' + website
    
    html = fetch_website(website)
    if html:
        cands = extract_from_html(html)
        if cands:
            # Save to DB
            with engine.begin() as c:
                c.execute(text("""
                    UPDATE companies SET vergi_no = :vkn 
                    WHERE company_id = :cid AND (vergi_no IS NULL OR vergi_no = '')
                """), {"vkn": cands[0], "cid": company_id})
            found += 1
            print(f"  [{i+1}/{len(rows)}] VKN bulundu: {name[:40]} -> {cands[0]}")
    else:
        errors += 1
    
    if (i+1) % 20 == 0:
        print(f"Ilerleme: {i+1}/{len(rows)}, Bulunan: {found}, Hata: {errors}")
    
    time.sleep(0.5)  # Rate limiting

print(f"\nSonuc: {found} VKN bulundu, {errors} hata, toplam {len(rows)} firma")
