from sqlalchemy import create_engine, text
import os
import re
import unicodedata
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

def normalize_name(name: str) -> str:
    if not name:
        return ""
    s = unicodedata.normalize('NFC', str(name))
    s = s.strip()
    s = ' '.join(s.split())
    
    replacements = [
        # Company types
        (r'\bA\.?S\.?\b', 'AS'),
        (r'\bLTD\.?\s*STI\.?\b', 'LTD STI'),
        (r'\bLTD\.?\s*ŞTİ\.?\b', 'LTD STI'),
        (r'\bLIMITED\.?\s*SIRKETI\.?\b', 'LTD STI'),
        (r'\bANONIM\.?\s*SIRKETI\.?\b', 'AS'),
        
        # Activity
        (r'\bSAN\.?\s*VE\.?\s*TIC\.?\b', 'SAN VE TIC'),
        (r'\bSAN\.?\s*TIC\.?\b', 'SAN TIC'),
        (r'\bITH\.?\s*IHR\.?\b', 'ITH IHR'),
        (r'\bINS\.?\s*SAN\.?\s*TIC\.?\b', 'INS SAN TIC'),
        (r'\bMUH\.?\s*MIM\.?\b', 'MUH MIM'),
        (r'\bTUR\.?\s*TIC\.?\b', 'TUR TIC'),
        (r'\bGIDA\s*SAN\.?\s*TIC\.?\b', 'GIDA SAN TIC'),
        (r'\bTEK\.?\s*SAN\.?\s*TIC\.?\b', 'TEK SAN TIC'),
        (r'\bNAK\.?\s*TIC\.?\b', 'NAK TIC'),
        
        # ELEKTRONIK -> ELEK (specific first)
        (r'\bELEKTRONİK\b', 'ELEK'),
        (r'ELEKTRONİK\.', 'ELEK'),
        
        # ELEK with dot
        (r'ELEK\.', 'ELEK'),
        (r'\bELEK\b', 'ELEK'),
        
        # Other abbreviations
        (r'\bINS\.?\b', 'INS'),
        (r'\bTIC\.?\b', 'TIC'),
        (r'\bMUH\.?\b', 'MUH'),
        (r'\bMIM\.?\b', 'MIM'),
        
        # Generic
        (r'\bSAN\.?\s*VE\.?\s*TIC\.?\b', 'SAN VE TIC'),
        (r'\bSAN\.?\s*TIC\.?\b', 'SAN TIC'),
        (r'\bITH\.?\s*IHR\.?\b', 'ITH IHR'),
        (r'\bINS\.?\s*SAN\.?\s*TIC\.?\b', 'INS SAN TIC'),
        (r'\bMUH\.?\s*MIM\.?\b', 'MUH MIM'),
        (r'\bTUR\.?\s*TIC\.?\b', 'TUR TIC'),
        (r'\bGIDA\s*SAN\.?\s*TIC\.?\b', 'GIDA SAN TIC'),
        (r'\bTEK\.?\s*SAN\.?\s*TIC\.?\b', 'TEK SAN TIC'),
        (r'\bNAK\.?\s*TIC\.?\b', 'NAK TIC'),
    ]
    
    for pattern, repl in replacements:
        s = re.sub(pattern, repl, s, flags=re.IGNORECASE)
    
    tr_map = str.maketrans('gusiocGUSIOC', 'gusiocGUSIOC')
    s = s.translate(tr_map)
    return s.upper()

def normalize_tax_number(tax: str) -> str:
    if not tax:
        return ""
    return re.sub(r'\D', '', str(tax))

# Main matching
with engine.connect() as conn:
    # Load companies
    companies = conn.execute(text("SELECT company_id, legal_name, tax_number FROM companies")).fetchall()
    
    tax_map = {}
    name_map = {}
    name_multi = set()
    
    for row in companies:
        if row.tax_number:
            tax_norm = re.sub(r'\D', '', str(row.tax_number))
            if tax_norm:
                tax_map[tax_norm] = row.company_id
        
        norm = normalize_name(row.legal_name)
        if norm:
            if norm in name_map:
                name_multi.add(norm)
            else:
                name_map[norm] = row.company_id
    
    print(f"Companies loaded: {len(companies)}")
    print(f"Tax map: {len(tax_map)}")
    print(f"Name map (unique): {len(name_map) - len(name_multi)}")
    print(f"Name multi (conflict): {len(name_multi)}")
    
    # Get orphans
    orphans = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.raw_tax_number
        FROM source_records sr
        WHERE sr.company_id IS NULL
    """)).fetchall()
    
    print(f"\nTotal orphans: {len(orphans)}")
    
    # Match
    tax_matches = 0
    name_matches = 0
    multi_matches = 0
    no_matches = 0
    updates = []
    
    for row in orphans:
        src_id = row.source_record_id
        raw_name = row.raw_name
        raw_tax = row.raw_tax_number
        
        matched_id = None
        match_type = None
        
        if raw_tax:
            tax_norm = re.sub(r'\D', '', str(raw_tax))
            if tax_norm in tax_map:
                matched_id = tax_map[tax_norm]
                match_type = "tax"
        
        if matched_id is None and raw_name:
            norm_name = normalize_name(raw_name)
            if norm_name in name_map:
                if norm_name not in name_multi:
                    matched_id = name_map[norm_name]
                    match_type = "name_exact"
                else:
                    match_type = "name_multiple"
        
        if matched_id:
            updates.append((src_id, matched_id, match_type))
            if match_type == "tax":
                pass
            elif match_type == "name_exact":
                pass
            elif match_type == "name_multiple":
                pass
        else:
            no_matches += 1
    
    print(f"\nMatch results:")
    print(f"  Tax matches: {tax_matches}")
    print(f"  Name exact matches: {name_matches}")
    print(f"  Name multiple (ambiguous): {multi_matches}")
    print(f"  No match: {no_matches}")
    print(f"  Total processed: {len(orphans)}")
    
    # Apply updates
    if updates:
        print(f"\nApplying {len(updates)} updates...")
        with engine.begin() as conn:
            for src_id, comp_id, mtype in updates:
                conn.execute(
                    text("UPDATE source_records SET company_id = :cid WHERE source_record_id = :sid"),
                    {"cid": comp_id, "sid": src_id}
                )
        print("Updates applied.")
    
    # Verify
    with engine.connect() as conn:
        remaining = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE company_id IS NULL")).scalar()
        print(f"\nRemaining orphans: {remaining}")
        
        # By source
        rows = conn.execute(text("""
            SELECT s.source_name, COUNT(*) as cnt
            FROM source_records sr
            JOIN sources s ON sr.source_id = s.source_id
            WHERE sr.company_id IS NULL
            GROUP BY s.source_name
            ORDER BY cnt DESC
        """)).fetchall()
        print("\nRemaining orphans by source:")
        for r in rows:
            print(f"  {r[0]}: {r[1]}")