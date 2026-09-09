import sys
sys.path.insert(0, 'src')
from company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    # Check non-empty web_sitesi values
    r = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE raw_payload->>'web_sitesi' IS NOT NULL AND raw_payload->>'web_sitesi' != ''")).scalar()
    print(f'Source records with non-empty web_sitesi: {r}')
    
    # Check non-empty vergi_no values
    r2 = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE raw_payload->>'vergi_no' IS NOT NULL AND raw_payload->>'vergi_no' != ''")).scalar()
    print(f'Source records with non-empty vergi_no: {r2}')
    
    # Check non-empty adres values
    r3 = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE raw_payload->>'adres' IS NOT NULL AND raw_payload->>'adres' != ''")).scalar()
    print(f'Source records with non-empty adres: {r3}')
    
    # Check non-empty emailler values
    r4 = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE raw_payload->>'emailler' IS NOT NULL AND raw_payload->>'emailler' != ''")).scalar()
    print(f'Source records with non-empty emailler: {r4}')
    
    # Check non-empty telefonler values
    r5 = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE raw_payload->>'telefonler' IS NOT NULL AND raw_payload->>'telefonler' != ''")).scalar()
    print(f'Source records with non-empty telefonler: {r5}')
    
    # Companies with primary_email populated
    r6 = conn.execute(text("SELECT COUNT(*) FROM companies WHERE primary_email IS NOT NULL AND primary_email != ''")).scalar()
    print(f'Companies with primary_email populated: {r6}')
    
    # Companies with primary_phone populated
    r7 = conn.execute(text("SELECT COUNT(*) FROM companies WHERE primary_phone IS NOT NULL AND primary_phone != ''")).scalar()
    print(f'Companies with primary_phone populated: {r7}')
    
    # Check sample web_sitesi values
    r8 = conn.execute(text("SELECT raw_payload->>'web_sitesi' FROM source_records WHERE raw_payload->>'web_sitesi' IS NOT NULL AND raw_payload->>'web_sitesi' != '' LIMIT 5")).fetchall()
    print(f'\nSample web_sitesi values:')
    for row in r8:
        print(f'  {row[0]}')
    
    # Check sample vergi_no values
    r9 = conn.execute(text("SELECT raw_payload->>'vergi_no' FROM source_records WHERE raw_payload->>'vergi_no' IS NOT NULL AND raw_payload->>'vergi_no' != '' LIMIT 5")).fetchall()
    print(f'\nSample vergi_no values:')
    for row in r9:
        print(f'  {row[0]}')
