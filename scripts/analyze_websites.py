#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text
from collections import Counter

eng = get_engine()
with eng.connect() as conn:
    # Get all websites for companies without VKN
    rows = conn.execute(text("""
        SELECT c.company_id, c.legal_name, c.website_domain
        FROM companies c
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND COALESCE(c.tax_number, c.vergi_no) IS NULL
        AND c.website_domain IS NOT NULL AND c.website_domain != ''
    """)).fetchall()
    
    print(f"VKN'suz ama web sitesi olan firma: {len(rows)}")
    
    # Analyze domains
    domains = []
    for r in rows:
        domain = r[2].lower()
        # Extract domain from URL
        if '://' in domain:
            domain = domain.split('://')[1]
        if '/' in domain:
            domain = domain.split('/')[0]
        domains.append(domain)
    
    # Count TLDs
    tlds = Counter(d.split('.')[-1] for d in domains)
    print('\nEn yaygin TLDler:')
    for tld, count in tlds.most_common(10):
        print(f'  .{tld}: {count}')
    
    # Filter out generic portals
    generic = ['isim.org.tr', 'osp.com.tr', 'ostim.org.tr', 'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com']
    specific = [r for r in rows if not any(g in r[2].lower() for g in generic)]
    print(f'\nGeneric portal haric: {len(specific)} firma')
    
    # Show top 20 specific domains
    specific_domains = Counter()
    for r in specific:
        domain = r[2].lower()
        if '://' in domain:
            domain = domain.split('://')[1]
        if '/' in domain:
            domain = domain.split('/')[0]
        specific_domains[domain] += 1
    
    print('\nEn yaygin ozel domainler:')
    for domain, count in specific_domains.most_common(20):
        print(f'  {domain}: {count}')
