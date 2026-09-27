import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    
    # Check ALL rows where nace_validity is not one of the known tags
    result = conn.execute(text("""
        SELECT nace_validity, COUNT(*) as cnt
        FROM companies
        WHERE nace_validity NOT IN ('fallback', 'medium', 'title_default', 'unknown')
        GROUP BY nace_validity
        ORDER BY COUNT(*) DESC
    """)).fetchall()
    
    print('All distinct nace_validity values (excluding known tags):')
    for row in result:
        print(f'  {row[0]}: {row[1]}')