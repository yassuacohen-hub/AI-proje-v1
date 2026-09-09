"""ERSUTEK firma detayli hex kontrolu."""
from company_master.db.connection import get_engine
from sqlalchemy import text
import re

eng = get_engine()
conn = eng.connect()

rows = conn.execute(text("""
    SELECT legal_name, trade_name, vergi_no
    FROM companies
    WHERE is_ankara=TRUE AND is_osb_member=TRUE
      AND legal_name LIKE '%ERSUTEK%'
    LIMIT 3
""")).mappings().all()

for r in rows:
    name = r['legal_name']
    print(f"---")
    print(f"legal_name repr: {repr(name)}")
    print(f"legal_name hex: {name.encode('utf-8').hex()}")
    # Karakter karakter kontrol
    for i, ch in enumerate(name):
        if ord(ch) < 32 or ord(ch) > 126:
            print(f"  Pozisyon {i}: {repr(ch)} (U+{ord(ch):04X})")
    
    # normalize_company_name test
    cleaned = re.sub(r'[\r\n\t]+', ' ', name)
    cleaned = re.sub(r'\s{2,}', ' ', cleaned)
    result = cleaned.upper().strip()
    print(f"normalize sonuc: {repr(result)}")

conn.close()