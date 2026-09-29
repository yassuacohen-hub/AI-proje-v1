import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    result = conn.execute(text('SELECT COUNT(*) FROM companies')).scalar()
    print(f'Total companies: {result}')
    
    result = conn.execute(text('SELECT COUNT(*) FROM companies WHERE nace_code IS NOT NULL')).scalar()
    print(f'Companies with nace_code: {result}')
    
    result = conn.execute(text('SELECT COUNT(*) FROM companies WHERE nace_code IS NULL')).scalar()
    print(f'Companies with NULL nace_code: {result}')
    
    result = conn.execute(text('SELECT nace_code, COUNT(*) as cnt FROM companies WHERE nace_code IS NOT NULL GROUP BY nace_code ORDER BY cnt DESC')).fetchall()
    print(f'Total unique nace_code values: {len(result)}')
    for row in result[:20]:
        print(f'  {row[0]}: {row[1]}')