import sys
sys.path.insert(0, 'src')
from company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    # Check how many companies have adres populated
    r = conn.execute(text("SELECT COUNT(*) FROM companies WHERE adres IS NOT NULL AND adres != ''")).scalar()
    print(f'Companies with adres populated: {r}')
    
    # Check how many source records have adres in payload
    r2 = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE raw_payload->>'adres' IS NOT NULL")).scalar()
    print(f'Source records with adres in payload: {r2}')
    
    # Check how many companies have website_domain populated
    r3 = conn.execute(text("SELECT COUNT(*) FROM companies WHERE website_domain IS NOT NULL AND website_domain != ''")).scalar()
    print(f'Companies with website_domain populated: {r3}')
    
    # Check how many source records have web_sitesi or website in payload
    r4 = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE raw_payload->>'web_sitesi' IS NOT NULL OR raw_payload->>'website' IS NOT NULL")).scalar()
    print(f'Source records with website in payload: {r4}')
    
    # Check how many companies have tax_number populated
    r5 = conn.execute(text("SELECT COUNT(*) FROM companies WHERE tax_number IS NOT NULL AND tax_number != ''")).scalar()
    print(f'Companies with tax_number populated: {r5}')
    
    # Check how many source records have vergi_no or tax_number in payload
    r6 = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE raw_payload->>'vergi_no' IS NOT NULL OR raw_payload->>'tax_number' IS NOT NULL")).scalar()
    print(f'Source records with tax_number in payload: {r6}')
    
    # Check all distinct keys in raw_payload
    r7 = conn.execute(text("""
        SELECT DISTINCT jsonb_object_keys(raw_payload) as key
        FROM source_records
        WHERE raw_payload IS NOT NULL
        ORDER BY key
    """)).fetchall()
    print(f'\nAll distinct keys in raw_payload:')
    for row in r7:
        print(f'  {row[0]}')
    
    # Count occurrences of each key
    r8 = conn.execute(text("""
        SELECT jsonb_object_keys(raw_payload) as key, COUNT(*) as cnt
        FROM source_records
        WHERE raw_payload IS NOT NULL
        GROUP BY jsonb_object_keys(raw_payload)
        ORDER BY cnt DESC
    """)).fetchall()
    print(f'\nKey occurrence counts:')
    for row in r8:
        print(f'  {row[0]}: {row[1]}')
