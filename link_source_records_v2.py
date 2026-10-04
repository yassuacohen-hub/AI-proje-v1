#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VERI-KAYNAK-BAG-01 completion: Link remaining unlinked source_records to companies.

Efficient approach: Load all data to Python, match in memory, batch update.
"""

import sys
sys.path.insert(0, 'src')

from company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()

def get_all_data():
    """Load all needed data to memory."""
    with engine.connect() as conn:
        # Unlinked source_records
        r = conn.execute(text('''
            SELECT sr.source_record_id, s.source_name, sr.raw_name, sr.raw_tax_number, 
                   sr.raw_website, sr.raw_email, sr.raw_phone
            FROM source_records sr
            JOIN sources s ON sr.source_id = s.source_id
            WHERE sr.company_id IS NULL
        '''))
        unlinked = r.fetchall()
        
        # All companies
        r = conn.execute(text('''
            SELECT company_id, legal_name, trade_name, tax_number, website_domain,
                   primary_email, primary_phone
            FROM companies
        '''))
        companies = r.fetchall()
        
    return unlinked, companies

def build_company_indexes(companies):
    """Build lookup indexes for companies."""
    by_website = {}
    by_tax = {}
    by_email = {}
    by_phone = {}
    by_name = {}
    
    for c in companies:
        cid, legal, trade, tax, web, email, phone = c
        
        if web:
            by_website[web.strip().lower()] = cid
        
        if tax:
            by_tax[tax.strip()] = cid
            
        if email:
            by_email[email.strip().lower()] = cid
            
        if phone:
            by_phone[phone.strip()] = cid
            
        if legal:
            # Store by words in legal name for fuzzy matching
            words = legal.strip().lower().split()
            for w in words:
                if len(w) > 3:
                    by_name.setdefault(w, []).append(cid)
    
    return by_website, by_tax, by_email, by_phone, by_name

def main():
    print("=" * 70)
    print("VERI-KAYNAK-BAG-01: Linking unlinked source_records (efficient)")
    print("=" * 70)
    
    print("Loading data...")
    unlinked, companies = get_all_data()
    print(f"  Unlinked records: {len(unlinked)}")
    print(f"  Companies: {len(companies)}")
    
    print("Building company indexes...")
    by_website, by_tax, by_email, by_phone, by_name = build_company_indexes(companies)
    print(f"  Website index: {len(by_website)}")
    print(f"  Tax index: {len(by_tax)}")
    print(f"  Email index: {len(by_email)}")
    print(f"  Phone index: {len(by_phone)}")
    print(f"  Name words: {len(by_name)}")
    
    # Find matches
    updates = []
    matched_by = {"website": 0, "tax": 0, "email": 0, "phone": 0, "name": 0}
    
    for sr in unlinked:
        sid, src_name, raw_name, raw_tax, raw_web, raw_email, raw_phone = sr
        
        company_id = None
        match_type = None
        
        # Try exact website match
        if raw_web:
            web = raw_web.strip().lower()
            if web in by_website:
                company_id = by_website[web]
                match_type = "website"
        
        # Try tax number
        if not company_id and raw_tax:
            tax = raw_tax.strip()
            if tax in by_tax:
                company_id = by_tax[tax]
                match_type = "tax"
        
        # Try email
        if not company_id and raw_email:
            email = raw_email.strip().lower()
            if email in by_email:
                company_id = by_email[email]
                match_type = "email"
        
        # Try phone
        if not company_id and raw_phone:
            phone = raw_phone.strip()
            if phone in by_phone:
                company_id = by_phone[phone]
                match_type = "phone"
        
        # Try fuzzy name (use first significant word from raw_name)
        if not company_id and raw_name:
            words = raw_name.strip().lower().split()
            for w in words:
                if len(w) > 4 and w in by_name:
                    # Use first match
                    company_id = by_name[w][0]
                    match_type = "name"
                    break
        
        if company_id:
            updates.append((sid, company_id, match_type))
            matched_by[match_type] += 1
    
    print(f"\nFound matches: {len(updates)}")
    for k, v in matched_by.items():
        if v:
            print(f"  {k}: {v}")
    
    # Batch update
    if updates:
        print("\nUpdating database...")
        batch_size = 500
        with engine.begin() as conn:
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i+batch_size]
                for sid, cid, _ in batch:
                    conn.execute(text('''
                        UPDATE source_records 
                        SET company_id = :cid 
                        WHERE source_record_id = :sid
                    '''), {"cid": cid, "sid": sid})
                if (i // batch_size + 1) % 10 == 0:
                    print(f"  Processed: {min(i+batch_size, len(updates))}/{len(updates)}")
        
        print("Database update complete!")
    
    # Final check
    with engine.connect() as conn:
        r = conn.execute(text('''
            SELECT s.source_name, COUNT(*) as cnt
            FROM source_records sr
            JOIN sources s ON sr.source_id = s.source_id
            WHERE sr.company_id IS NULL
            GROUP BY s.source_name
            ORDER BY cnt DESC
        '''))
        print("\nFinal unlinked counts:")
        for row in r:
            print(f"  {row[0]}: {row[1]}")
        
        r = conn.execute(text('SELECT COUNT(*) FROM source_records WHERE company_id IS NOT NULL'))
        print(f"\nTotal linked: {r.scalar()}")
        r = conn.execute(text('SELECT COUNT(*) FROM source_records'))
        print(f"Total records: {r.scalar()}")

if __name__ == "__main__":
    main()