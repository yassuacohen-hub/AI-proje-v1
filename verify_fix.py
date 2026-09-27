import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    
    # Check remaining invalid nace_validity
    result = conn.execute(text("SELECT COUNT(*) FROM companies WHERE nace_validity ~ '^\d{2}\.\d{2}(\.\d{2})?$' AND nace_validity NOT IN ('fallback', 'medium', 'title_default', 'unknown')")).scalar()
    print(f'Remaining invalid nace_validity: {result}')
    
    result = conn.execute(text("SELECT COUNT(*) FROM companies WHERE nace_validity = 'fallback'")).scalar()
    print(f'Rows with fallback: {result}')
    
    result = conn.execute(text("SELECT COUNT(*) FROM companies WHERE nace_validity IS NULL")).scalar()
    print(f'NULL nace_validity: {result}')
    
    result = conn.execute(text("SELECT nace_source, COUNT(*) FROM companies GROUP BY nace_source ORDER BY COUNT(*) DESC")).fetchall()
    for row in result:
        print(f'{row[0]}: {row[1]}')