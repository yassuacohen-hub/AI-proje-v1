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

with engine.connect() as conn:
    # Compare specific pairs
    # Check if "3DTİM ELEKTRONİK A.Ş." in companies matches source_records
    rows = conn.execute(text("""
        SELECT company_id, legal_name
        FROM companies
        WHERE legal_name ILIKE '%3dtim%'
    """)).fetchall()
    print("Companies with '3dtim':")
    for r in rows:
        print(f"  {r[0]} | {r[1]}")
    
    rows = conn.execute(text("""
        SELECT source_record_id, raw_name
        FROM source_records
        WHERE raw_name ILIKE '%3dtim%'
    """)).fetchall()
    print("\nSource records with '3dtim':")
    for r in rows:
        print(f"  {r[0]} | {r[1]}")
    
    # Check the actual codepoints
    print("\nCodepoint analysis:")
    test_name = "3DTİM ELEKTRONİK A.Ş."
    print(f"Test: {test_name}")
    for c in test_name:
        print(f"  {c} = U+{ord(c):04X}")
    
    # Check one from source_records
    rows = conn.execute(text("SELECT raw_name FROM source_records WHERE raw_name ILIKE '%3dtim%' LIMIT 1")).fetchall()
    if rows:
        name = rows[0][0]
        print(f"\nSource record: {name}")
        for c in name:
            print(f"  {c} = U+{ord(c):04X}")