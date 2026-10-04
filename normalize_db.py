from sqlalchemy import create_engine, text
import os
import re
import unicodedata
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

# Update companies legal_name to NFC in Python
with engine.connect() as conn:
    rows = conn.execute(text("SELECT company_id, legal_name FROM companies WHERE legal_name IS NOT NULL")).fetchall()
    print(f"Processing {len(rows)} companies...")
    updated = 0
    for row in rows:
        company_id = row.company_id
        legal_name = row.legal_name
        if legal_name:
            nfc_name = unicodedata.normalize('NFC', legal_name)
            if nfc_name != legal_name:
                conn.execute(
                    text("UPDATE companies SET legal_name = :name WHERE company_id = :id"),
                    {"name": nfc_name, "id": company_id}
                )
                updated += 1
    conn.commit()
    print(f"Companies updated: {updated}")

# Update source_records raw_name to NFC
with engine.connect() as conn:
    rows = conn.execute(text("SELECT source_record_id, raw_name FROM source_records WHERE raw_name IS NOT NULL")).fetchall()
    print(f"Processing {len(rows)} source records...")
    updated = 0
    for row in rows:
        src_id = row.source_record_id
        raw_name = row.raw_name
        if raw_name:
            nfc_name = unicodedata.normalize('NFC', raw_name)
            if nfc_name != raw_name:
                conn.execute(
                    text("UPDATE source_records SET raw_name = :name WHERE source_record_id = :id"),
                    {"name": nfc_name, "id": src_id}
                )
                updated += 1
    conn.commit()
    print(f"Source records updated: {updated}")

# Now test matching
import re
import unicodedata

def normalize_name(name: str) -> str:
    if not name:
        return ""
    s = unicodedata.normalize('NFC', str(name))
    s = s.strip()
    s = ' '.join(s.split())
    replacements = {
        r'\bA\.?S\.?\b': 'AS',
        r'\bLTD\.?\s*STI\.?\b': 'LTD STI',
        r'\bLTD\.?\s*ŞTİ\.?\b': 'LTD STI',
        r'\bLIMITED\.?\s*SIRKETI\.?\b': 'LTD STI',
        r'\bANONIM\.?\s*SIRKETI\.?\b': 'AS',
        r'\bSAN\.?\s*VE\.?\s*TIC\.?\b': 'SAN VE TIC',
        r'\bSAN\.?\s*TIC\.?\b': 'SAN TIC',
        r'\bITH\.?\s*IHR\.?\b': 'ITH IHR',
        r'\bINS\.?\s*SAN\.?\s*TIC\.?\b': 'INS SAN TIC',
        r'\bMUH\.?\s*MIM\.?\b': 'MUH MIM',
        r'\bTUR\.?\s*TIC\.?\b': 'TUR TIC',
        r'\bGIDA\s*SAN\.?\s*TIC\.?\b': 'GIDA SAN TIC',
        r'\bTEK\.?\s*SAN\.?\s*TIC\.?\b': 'TEK SAN TIC',
        r'\bNAK\.?\s*TIC\.?\b': 'NAK TIC',
        r'\bELEK\.?\b': 'ELEK',
        r'\bINS\.?\b': 'INS',
        r'\bTIC\.?\b': 'TIC',
        r'\bMUH\.?\b': 'MUH',
        r'\bMIM\.?\b': 'MIM',
    }
    for pattern, repl in replacements.items():
        s = re.sub(pattern, repl, s, flags=re.IGNORECASE)
    tr_map = str.maketrans('gusiocGUSIOC', 'gusiocGUSIOC')
    s = s.translate(tr_map)
    return s.upper()

def normalize_tax_number(tax: str) -> str:
    if not tax:
        return ""
    return re.sub(r'\D', '', str(tax))

# Test matching
with engine.connect() as conn:
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
    
    print(f"Companies loaded: {len(name_map)} unique names, {len(tax_map)} tax numbers")
    
    orphans = conn.execute(text("SELECT source_record_id, raw_name, raw_tax_number FROM source_records WHERE company_id IS NULL")).fetchall()
    print(f"Total orphans: {len(orphans)}")
    
    name_matches = 0
    no_matches = 0
    updates = []
    
    for row in conn.execute(text("SELECT source_record_id, raw_name, raw_tax_number FROM source_records WHERE company_id IS NULL")).fetchall():
        src_id = row.source_record_id
        raw_name = row.raw_name
        raw_tax = row.raw_tax_number
        
        matched_id = None
        match_type = None
        
        if raw_tax:
            tax_norm = re.sub(r'\D', '', str(raw_tax))
            if tax_norm in tax_map:
                matched_id = tax_map[tax_norm]
        
        if matched_id is None and raw_name:
            norm_name = normalize_name(raw_name)
            if norm_name in name_map:
                if norm_name not in name_multi:
                    matched_id = name_map[norm_name]
                    match_type = "name_exact"
                else:
                    match_type = "name_multiple"
        
        if matched_id:
            if match_type == "name_exact":
                pass
        else:
            pass
    
    print("Matching test complete - check results")