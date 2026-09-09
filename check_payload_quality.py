import sys
sys.path.insert(0, 'src')
from company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    sample = conn.execute(text("""
        SELECT raw_payload 
        FROM source_records 
        WHERE raw_payload IS NOT NULL 
        LIMIT 5
    """)).mappings().all()
    
    print("Sample raw_payload keys:")
    for r in sample:
        payload = r['raw_payload']
        if payload:
            print(f"  Keys: {list(payload.keys())[:10]}")
    
    addr_in_payload = conn.execute(text("""
        SELECT COUNT(*) 
        FROM source_records sr
        JOIN companies c ON c.source_record_id = sr.source_record_id
        WHERE sr.raw_payload->>'adres' IS NOT NULL 
        AND (c.adres IS NULL OR c.adres = '')
    """)).scalar()
    print(f"\nAddress in payload but not in companies: {addr_in_payload}")
    
    web_in_payload = conn.execute(text("""
        SELECT COUNT(*) 
        FROM source_records sr
        JOIN companies c ON c.source_record_id = sr.source_record_id
        WHERE (sr.raw_payload->>'web_sitesi' IS NOT NULL OR sr.raw_payload->>'website' IS NOT NULL)
        AND (c.website_domain IS NULL OR c.website_domain = '')
    """)).scalar()
    print(f"Website in payload but not in companies: {web_in_payload}")
    
    vergi_in_payload = conn.execute(text("""
        SELECT COUNT(*) 
        FROM source_records sr
        JOIN companies c ON c.source_record_id = sr.source_record_id
        WHERE (sr.raw_payload->>'vergi_no' IS NOT NULL OR sr.raw_payload->>'tax_number' IS NOT NULL)
        AND (c.tax_number IS NULL OR c.tax_number = '')
    """)).scalar()
    print(f"Tax number in payload but not in companies: {vergi_in_payload}")
    
    total_sr = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE raw_payload IS NOT NULL")).scalar()
    print(f"\nTotal source_records with payload: {total_sr}")
