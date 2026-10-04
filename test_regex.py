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

# Test the normalization
src = "3DTİM ELEKTRONİK A.Ş."
company = "3DTİM ELEK. A.Ş."

print(f"Source: {src}")
print(f"Company: {company}")
print(f"Source normalized: {normalize_name(src)}")
print(f"Company normalized: {normalize_name(company)}")
print(f"Match: {normalize_name(src) == normalize_name(company)}")

# Test the regex replacements step by step
import re
s = "3DTİM ELEKTRONİK A.Ş."
print(f"\nStep by step:")
print(f"Original: {s}")
s = re.sub(r'\bA\.?S\.?\b', 'AS', s, flags=re.IGNORECASE)
print(f"After A.S.: {s}")
s = re.sub(r'\bELEK\.?\b', 'ELEK', s, flags=re.IGNORECASE)
print(f"After ELEK.: {s}")