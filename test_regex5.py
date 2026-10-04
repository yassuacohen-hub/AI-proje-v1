import re

def normalize_name(name: str) -> str:
    if not name:
        return ""
    s = name
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
        (r'ELEKTRONİK\.', 'ELEK'),  # no word boundary after dot
        
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

# Test
src = "3DTİM ELEKTRONİK A.Ş."
company = "3DTİM ELEK. A.Ş."

print(f"Source normalized: {normalize_name(src)}")
print(f"Company normalized: {normalize_name(company)}")
print(f"Match: {normalize_name(src) == normalize_name(company)}")