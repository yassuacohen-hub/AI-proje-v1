import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    # Check valid nace_codes
    result = conn.execute(text('SELECT nace_code FROM nace_codes')).fetchall()
    valid_codes = {row[0] for row in result}
    print(f'Valid nace_codes in reference table: {len(valid_codes)}')
    
    # Get all company nace_codes
    result = conn.execute(text('SELECT DISTINCT nace_code FROM companies WHERE nace_code IS NOT NULL')).fetchall()
    company_codes = {row[0] for row in result}
    print(f'Unique company nace_codes: {len(company_codes)}')
    
    # Find invalid codes
    invalid_codes = set()
    for code in company_codes:
        if code not in valid_codes:
            invalid_codes.add(code)
    
    print(f'Invalid codes count: {len(invalid_codes)}')
    for code in sorted(invalid_codes):
        print(f'  {code}')