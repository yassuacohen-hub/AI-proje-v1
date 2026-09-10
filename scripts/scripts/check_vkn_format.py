#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    # Check VKN format
    rows = conn.execute(text("""
        SELECT vergi_no, COUNT(*) as cnt 
        FROM companies 
        WHERE vergi_no IS NOT NULL AND vergi_no != ''
        GROUP BY vergi_no 
        ORDER BY cnt DESC 
        LIMIT 20
    """)).fetchall()
    print('En yaygin VKNler:')
    for row in rows:
        print(f'  {row[0]}: {row[1]} firma')
    
    # Check tax_number format
    rows2 = conn.execute(text("""
        SELECT tax_number, COUNT(*) as cnt 
        FROM companies 
        WHERE tax_number IS NOT NULL AND tax_number != ''
        GROUP BY tax_number 
        ORDER BY cnt DESC 
        LIMIT 10
    """)).fetchall()
    print('\nEn yaygin tax_number:')
    for row in rows2:
        print(f'  {row[0]}: {row[1]} firma')
    
    # Check VKN length distribution
    rows3 = conn.execute(text("""
        SELECT LENGTH(vergi_no) as len, COUNT(*) as cnt
        FROM companies
        WHERE vergi_no IS NOT NULL AND vergi_no != ''
        GROUP BY LENGTH(vergi_no)
        ORDER BY len
    """)).fetchall()
    print('\nVKN uzunluk dagilimi:')
    for row in rows3:
        print(f'  {row[0]} karakter: {row[1]} firma')
