import sys
sys.path.insert(0, 'src')
from company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    # Check quality score breakdown for companies with/without nace_name
    r = conn.execute(text("""
        SELECT 
            COUNT(*) FILTER (WHERE nace_name IS NOT NULL AND nace_name != '') as with_nace,
            COUNT(*) FILTER (WHERE nace_name IS NULL OR nace_name = '') as without_nace,
            AVG(data_quality_score) FILTER (WHERE nace_name IS NOT NULL AND nace_name != '') as avg_with_nace,
            AVG(data_quality_score) FILTER (WHERE nace_name IS NULL OR nace_name = '') as avg_without_nace
        FROM companies
    """)).fetchone()
    print(f'NACE name impact on quality:')
    print(f'  With nace_name: {r[0]} companies, avg score: {r[2]}')
    print(f'  Without nace_name: {r[1]} companies, avg score: {r[3]}')
    
    # Check how many companies without nace_name have nace_name_tr in payload
    r2 = conn.execute(text("""
        SELECT COUNT(*) 
        FROM source_records sr
        JOIN companies c ON c.source_record_id = sr.source_record_id
        WHERE (c.nace_name IS NULL OR c.nace_name = '')
        AND sr.raw_payload->>'nace_name_tr' IS NOT NULL 
        AND sr.raw_payload->>'nace_name_tr' != ''
    """)).scalar()
    print(f'\nCompanies without nace_name but with nace_name_tr in payload: {r2}')
    
    # Check fields that could improve low-quality scores
    r3 = conn.execute(text("""
        SELECT 
            COUNT(*) FILTER (WHERE adres IS NULL OR adres = '') as no_adres,
            COUNT(*) FILTER (WHERE primary_email IS NULL OR primary_email = '') as no_email,
            COUNT(*) FILTER (WHERE primary_phone IS NULL OR primary_phone = '') as no_phone,
            COUNT(*) FILTER (WHERE website_domain IS NULL OR website_domain = '') as no_website,
            COUNT(*) FILTER (WHERE tax_number IS NULL OR tax_number = '') as no_tax,
            COUNT(*) FILTER (WHERE nace_name IS NULL OR nace_name = '') as no_nace
        FROM companies
        WHERE data_quality_score < 50
    """)).fetchone()
    print(f'\nLow quality companies (<50) missing fields:')
    print(f'  No adres: {r3[0]}')
    print(f'  No email: {r3[1]}')
    print(f'  No phone: {r3[2]}')
    print(f'  No website: {r3[3]}')
    print(f'  No tax_number: {r3[4]}')
    print(f'  No nace_name: {r3[5]}')
