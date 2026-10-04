# -*- coding: utf-8 -*-
"""VERI-SEKTOR-01: companies.sector_name ve companies.sector_source doldurma."""

import json
import os
import re
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

def is_aso_meslek_grubu(text: str) -> bool:
    if not text:
        return False
    return bool(re.match(r'^\d{1,2}\.\s*MESLEK\s+GRUBU$', text.strip(), re.IGNORECASE))

def normalize_sector(text: str) -> str:
    if not text:
        return ""
    s = str(text).strip()
    s = re.sub(r'\d+$', '', s)
    s = s.rstrip('. ')
    s = s.strip()
    return s

def get_display_name(normalized: str) -> str:
    if not normalized:
        return ""
    words = normalized.split()
    result = []
    for word in words:
        if word.isupper() and len(word) > 2:
            result.append(word)
        else:
            result.append(word.capitalize())
    return ' '.join(result)

def is_aso_meslek_grubu(text: str) -> bool:
    if not text:
        return False
    return bool(re.match(r'^\d{1,2}\.\s*MESLEK\s+GRUBU$', text.strip(), re.IGNORECASE))

def normalize_sector(text: str) -> str:
    if not text:
        return ""
    s = str(text).strip()
    s = re.sub(r'\d+$', '', s)
    s = s.rstrip('. ')
    s = s.strip()
    return s

def get_display_name(normalized: str) -> str:
    if not normalized:
        return ""
    words = normalized.split()
    result = []
    for word in words:
        if word.isupper() and len(word) > 2:
            result.append(word)
        else:
            result.append(word.capitalize())
    return ' '.join(result)

def is_aso_meslek_grubu(text: str) -> bool:
    if not text:
        return False
    return bool(re.match(r'^\d{1,2}\.\s*MESLEK\s+GRUBU$', text.strip(), re.IGNORECASE))

def normalize_sector(text: str) -> str:
    if not text:
        return ""
    s = str(text).strip()
    s = re.sub(r'\d+$', '', s)
    s = s.rstrip('. ')
    s = s.strip()
    return s

def get_display_name(normalized: str) -> str:
    if not normalized:
        return ""
    words = normalized.split()
    result = []
    for word in words:
        if word.isupper() and len(word) > 2:
            result.append(word)
        else:
            result.append(word.capitalize())
    return ' '.join(result)

def main():
    print("Populating companies.sector_name and sector_source...")
    
    # Load sector dictionary
    dict_path = Path("data/sektor/sektor_sozluk.json")
    if not dict_path.exists():
        print(f"Dictionary not found at {dict_path}")
        return
    
    with open(dict_path, 'r', encoding='utf-8') as f:
        sektor_sozluk = json.load(f)
    
    print(f"Loaded {len(sektor_sozluk)} sector entries from dictionary")
    
    # Build lookup map: normalized sector -> display_name
    sector_map = {}
    for entry in sektor_sozluk:
        norm = entry['sade']
        display = entry['gosterim']
        sector_map[norm] = display
    
    print(f"Built lookup map with {len(sector_map)} entries")
    
    # Get all companies with their sector info from source_records
    with engine.connect() as conn:
        # Get sector info for each company via source_records
        rows = conn.execute(text("""
            SELECT c.company_id, c.legal_name,
                   sr.raw_payload->>'sektor' as sektor_raw,
                   s.source_name
            FROM companies c
            JOIN source_records sr ON sr.company_id = c.company_id
            JOIN sources s ON sr.source_id = s.source_id
            WHERE sr.raw_payload->>'sektor' IS NOT NULL
            ORDER BY c.company_id, s.source_name
        """)).fetchall()
        
        print(f"Found {len(rows)} company-sector records from source_records")
        
        # Group by company_id, pick best sector match
        company_sectors = {}  # company_id -> {sector_norm: count}
        company_sources = {}  # company_id -> set of sources
        
        for row in rows:
            company_id = row[0]
            sektor_raw = row[2]
            source_name = row[3]
            
            if is_aso_meslek_grubu(sektor_raw):
                continue
            
            norm = normalize_sector(sektor_raw)
            if not norm:
                continue
            
            if company_id not in company_sectors:
                company_sectors[company_id] = {}
                company_sources[company_id] = set()
            
            company_sectors[company_id][norm] = company_sectors[company_id].get(norm, 0) + 1
            company_sources[company_id].add(source_name)
        
        print(f"Companies with sector info: {len(company_sectors)}")
        
        # For each company, pick most frequent sector
        updates = []
        for company_id, sector_counts in company_sectors.items():
            if not sector_counts:
                continue
            
            # Pick most frequent
            best_sector = max(sector_counts.items(), key=lambda x: x[1])[0]
            display_name = get_display_name(best_sector)
            sources = list(company_sources[company_id])
            source_str = ", ".join(sorted(sources))
            
            updates.append({
                'company_id': company_id,
                'sector_name': display_name,
                'sector_source': source_str
            })
        
        print(f"Prepared {len(updates)} company updates")
        
        # Apply updates
        if updates:
            print(f"Applying {len(updates)} updates...")
            batch_size = 500
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i+batch_size]
                with engine.begin() as conn:
                    for upd in batch:
                        conn.execute(text("""
                            UPDATE companies 
                            SET sector_name = :sector_name,
                                sector_source = :sector_source
                            WHERE company_id = :company_id
                        """), upd)
                print(f"  Updated {min(i+batch_size, len(updates))}/{len(updates)}")
            
            print("Updates applied successfully.")
        
        # Verify
        with engine.connect() as conn:
            total = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
            with_sector = conn.execute(text("SELECT COUNT(*) FROM companies WHERE sector_name IS NOT NULL")).scalar()
            print(f"\nVerification:")
            print(f"  Total companies: {total}")
            print(f"  With sector_name: {with_sector} ({with_sector/total*100:.1f}%)")
            
            # Sample
            samples = conn.execute(text("""
                SELECT company_id, legal_name, sector_name, sector_source
                FROM companies 
                WHERE sector_name IS NOT NULL
                LIMIT 10
            """)).fetchall()
            print("\nSample:")
            for s in samples:
                print(f"  {s[0]} | {s[1][:40]} | {s[2]} | {s[3][:50]}")

if __name__ == "__main__":
    import os
    from pathlib import Path
    import re
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    
    load_dotenv()
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    main()