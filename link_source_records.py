#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VERI-KAYNAK-BAG-01 completion: Link remaining unlinked source_records to companies.

Matches by:
1. website_domain (exact or partial)
2. raw_tax_number -> tax_number
3. raw_name -> legal_name (fuzzy)
"""

import sys
sys.path.insert(0, 'src')

from company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()

def link_by_website(source_name: str) -> int:
    """Link records by website_domain match."""
    with engine.begin() as conn:
        # Find matches
        r = conn.execute(text(f'''
            SELECT sr.source_record_id, c.company_id
            FROM source_records sr
            JOIN sources s ON sr.source_id = s.source_id
            JOIN companies c ON c.website_domain = sr.raw_website
            WHERE sr.company_id IS NULL 
            AND s.source_name = '{source_name}'
            AND sr.raw_website IS NOT NULL
        '''))
        matches = r.fetchall()
        
        if matches:
            for source_record_id, company_id in matches:
                conn.execute(text('''
                    UPDATE source_records 
                    SET company_id = :cid 
                    WHERE source_record_id = :sid
                '''), {"cid": company_id, "sid": source_record_id})
        
        return len(matches)

def link_by_website_partial(source_name: str) -> int:
    """Link records by partial website_domain match (for cases with multiple URLs)."""
    with engine.begin() as conn:
        # Find matches where raw_website contains the company's website_domain
        r = conn.execute(text(f'''
            SELECT sr.source_record_id, c.company_id
            FROM source_records sr
            JOIN sources s ON sr.source_id = s.source_id
            JOIN companies c ON c.website_domain IS NOT NULL
                AND (sr.raw_website ILIKE '%' || c.website_domain || '%' 
                     OR c.website_domain ILIKE '%' || sr.raw_website || '%')
            WHERE sr.company_id IS NULL 
            AND s.source_name = '{source_name}'
            AND sr.raw_website IS NOT NULL
        '''))
        matches = r.fetchall()
        
        if matches:
            for source_record_id, company_id in matches:
                conn.execute(text('''
                    UPDATE source_records 
                    SET company_id = :cid 
                    WHERE source_record_id = :sid
                '''), {"cid": company_id, "sid": source_record_id})
        
        return len(matches)

def link_by_tax_number(source_name: str) -> int:
    """Link records by raw_tax_number -> tax_number."""
    with engine.begin() as conn:
        r = conn.execute(text(f'''
            SELECT sr.source_record_id, c.company_id
            FROM source_records sr
            JOIN sources s ON sr.source_id = s.source_id
            JOIN companies c ON c.tax_number = sr.raw_tax_number
            WHERE sr.company_id IS NULL 
            AND s.source_name = '{source_name}'
            AND sr.raw_tax_number IS NOT NULL
            AND c.tax_number IS NOT NULL
        '''))
        matches = r.fetchall()
        
        if matches:
            for source_record_id, company_id in matches:
                conn.execute(text('''
                    UPDATE source_records 
                    SET company_id = :cid 
                    WHERE source_record_id = :sid
                '''), {"cid": company_id, "sid": source_record_id})
        
        return len(matches)

def link_by_name_fuzzy(source_name: str) -> int:
    """Link records by fuzzy name match (legal_name contains raw_name or vice versa)."""
    with engine.begin() as conn:
        r = conn.execute(text(f'''
            SELECT sr.source_record_id, c.company_id, sr.raw_name, c.legal_name
            FROM source_records sr
            JOIN sources s ON sr.source_id = s.source_id
            JOIN companies c ON c.legal_name ILIKE '%' || sr.raw_name || '%'
            WHERE sr.company_id IS NULL 
            AND s.source_name = '{source_name}'
            AND sr.raw_name IS NOT NULL
        '''))
        matches = r.fetchall()
        
        if matches:
            for row in matches:
                conn.execute(text('''
                    UPDATE source_records 
                    SET company_id = :cid 
                    WHERE source_record_id = :sid
                '''), {"cid": row[1], "sid": row[0]})
        
        return len(matches)

def get_unlinked_counts():
    """Get current unlinked counts by source."""
    with engine.connect() as conn:
        r = conn.execute(text('''
            SELECT s.source_name, COUNT(*) as cnt
            FROM source_records sr
            JOIN sources s ON sr.source_id = s.source_id
            WHERE sr.company_id IS NULL
            GROUP BY s.source_name
            ORDER BY cnt DESC
        '''))
        return {row[0]: row[1] for row in r}

def main():
    print("=" * 70)
    print("VERI-KAYNAK-BAG-01: Linking unlinked source_records to companies")
    print("=" * 70)
    
    print("\nInitial unlinked counts:")
    for src, cnt in get_unlinked_counts().items():
        print(f"  {src}: {cnt}")
    
    # Link ostim.org.tr by website (exact and partial)
    print("\n--- Linking ostim.org.tr ---")
    c1 = link_by_website('ostim.org.tr')
    c2 = link_by_website_partial('ostim.org.tr')
    print(f"  Exact website match: {c1}")
    print(f"  Partial website match: {c2}")
    
    # Link baskentosb.org.tr by website
    print("\n--- Linking baskentosb.org.tr ---")
    c3 = link_by_website('baskentosb.org.tr')
    c4 = link_by_website_partial('baskentosb.org.tr')
    print(f"  Exact website match: {c3}")
    print(f"  Partial website match: {c4}")
    
    # Link aso.org.tr (check what fields it has)
    print("\n--- Linking aso.org.tr ---")
    c5 = link_by_website('aso.org.tr')
    c6 = link_by_website_partial('aso.org.tr')
    c7 = link_by_tax_number('aso.org.tr')
    c8 = link_by_name_fuzzy('aso.org.tr')
    print(f"  Exact website match: {c5}")
    print(f"  Partial website match: {c6}")
    print(f"  Tax number match: {c7}")
    print(f"  Name fuzzy match: {c8}")
    
    print("\nFinal unlinked counts:")
    for src, cnt in get_unlinked_counts().items():
        print(f"  {src}: {cnt}")
    
    # Summary
    total_linked = c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8
    print(f"\nTotal newly linked: {total_linked}")

if __name__ == "__main__":
    main()