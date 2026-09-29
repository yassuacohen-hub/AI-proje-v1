import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    # Check all rows where nace_validity has NACE pattern
    result = conn.execute(text("""
        SELECT company_id, nace_validity, nace_code, nace_source
        FROM companies
        WHERE nace_validity ~ '^\d{2}\.\d{2}'
        ORDER BY nace_validity
    """)).fetchall()
    
    print(f'Total rows with NACE pattern in nace_validity: {len(result)}')
    for row in result:
        print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]}')