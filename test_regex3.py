import re

def normalize_name(name: str) -> str:
    if not name:
        return ""
    s = name
    s = s.strip()
    s = ' '.join(s.split())
    # Order matters - do specific replacements first
    replacements = [
        (r'\bA\.?S\.?\b', 'AS'),
        (r'\bLTD\.?\s*STI\.?\b', 'LTD STI'),
        (r'\bLTD\.?\s*ŞTİ\.?\b', 'LTD STI'),
        (r'\bLIMITED\.?\s*SIRKETI\.?\b', 'LTD STI'),
        (r'\bANONIM\.?\s*SIRKETI\.?\b', 'AS'),
        (r'\bSAN\.?\s*VE\.?\s*TIC\.?\b', 'SAN VE TIC'),
        (r'\bSAN\.?\s*TIC\.?\b', 'SAN TIC'),
        (r'\bITH\.?\s*IHR\.?\b', 'ITH IHR'),
        (r'\bINS\.?\s*SAN\.?\s*TIC\.?\b', 'INS SAN TIC'),
        (r'\bMUH\.?\s*MIM\.?\b', 'MUH MIM'),
        (r'\bTUR\.?\s*TIC\.?\b', 'TUR TIC'),
        (r'\bGIDA\s*SAN\.?\s*TIC\.?\b', 'GIDA SAN TIC'),
        (r'\bTEK\.?\s*SAN\.?\s*TIC\.?\b', 'TEK SAN TIC'),
        (r'\bNAK\.?\s*TIC\.?\b', 'NAK TIC'),
        # ELEKTRONIK -> ELEK (must be before generic ELEK)
        (r'\bELEKTRONİK\b', 'ELEK'),
        (r'\bELEKTRONIK\.\b', 'ELEK'),
        (r'\bELEK\.\b', 'ELEK'),
        (r'\bELEK\b', 'ELEK'),
        (r'\bELEK\.\b', 'ELEK'),
        (r'\bINS\.?\b', 'INS'),
        (r'\bTIC\.?\b', 'TIC'),
        (r'\bMUH\.?\b', 'MUH'),
        (r'\bMIM\.?\b', 'MIM'),
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

print(f"Source: {src}")
print(f"Company: {company}")

# Step by step
s = src
steps = [
    (r'\bELEKTRONİK\b', 'ELEK'),
    (r'\bELEKTRONİK\.\b', 'ELEK'),
    (r'\bELEK\.\b', 'ELEK'),
    (r'\bELEK\b', 'ELEK'),
    (r'\bA\.?S\.?\b', 'AS'),
]
for pattern, repl in steps:
    s = re.sub(pattern, repl, s, flags=re.IGNORECASE)
    print(f"After {pattern} -> {repl}: {s}")

print(f"\nFull normalize: {normalize_name('3DTİM ELEKTRONİK A.Ş.')}")
print(f"Full normalize company: {normalize_name('3DTİM ELEK. A.Ş.')}")