from sqlalchemy import create_engine, text
import os
import re
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

def norm_tax(tax):
    return re.sub(r'\D', '', str(tax)) if tax else ""

with engine.connect() as conn:
    # Get all tax numbers from both tables
    co_tax = conn.execute(text("SELECT company_id, tax_number FROM companies WHERE tax_number IS NOT NULL")).fetchall()
    sr_tax = conn.execute(text("SELECT source_record_id, raw_tax_number FROM source_records WHERE raw_tax_number IS NOT NULL")).fetchall()
    
    # Normalize
    co_map = {norm_tax(t): cid for cid, t in co_tax if norm_tax(t)}
    sr_map = {norm_tax(t): sid for sid, t in sr_tax if norm_tax(t)}
    
    print(f"Companies unique tax: {len(co_map)}")
    print(f"Sources unique tax: {len(sr_map)}")
    
    # Find matches
    matches = set(co_map.keys()) & set(sr_map.keys())
    print(f"Exact tax matches: {len(matches)}")
    
    if matches:
        for m in list(matches)[:10]:
            print(f"  {m}: company={co_map[m]}, source={sr_map[m]}")
    
    # Check name matches with simple normalization
    co_names = conn.execute(text("SELECT company_id, legal_name FROM companies WHERE legal_name IS NOT NULL")).fetchall()
    sr_names = conn.execute(text("SELECT source_record_id, raw_name FROM source_records WHERE raw_name IS NOT NULL AND company_id IS NULL")).fetchall()
    
    def simple_norm(s):
        return re.sub(r'\s+', '', str(s).upper()) if s else ""
    
    co_name_map = {}
    for cid, name in co_names:
        n = simple_norm(name)
        if n:
            co_name_map[n] = cid
    
    sr_name_map = {}
    for sid, name in sr_names:
        n = simple_norm(name)
        if n:
            sr_name_map[n] = sid
    
    name_matches = set(co_name_map.keys()) & set(sr_name_map.keys())
    print(f"\nSimple name matches: {len(name_matches)}")
    
    if name_matches:
        for m in list(name_matches)[:10]:
            print(f"  company={co_name_map[m]}, source={sr_name_map[m]}")
            # Show original names
            co_orig = next(name for cid, name in co_names if simple_norm(name) == m)
            sr_orig = next(name for sid, name in sr_names if simple_norm(name) == m)
            print(f"    co: '{co_orig}'")
            print(f"    sr: '{sr_orig}'")