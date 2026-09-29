import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    # Check for raw_nace values that might contain multiple codes
    result = conn.execute(text("""
        SELECT raw_nace, COUNT(*) as cnt
        FROM source_records 
        WHERE raw_nace IS NOT NULL
        GROUP BY raw_nace
        HAVING raw_nace LIKE '%,%' OR raw_nace LIKE '%;%' OR raw_nace LIKE '%/%' OR raw_nace LIKE '%|%'
        ORDER BY cnt DESC
        LIMIT 20
    """)).fetchall()
    print('Raw_nace values with potential separators:')
    for row in result:
        print(f'  {row[0]} (count: {row[1]})')
    
    # Also check total count and unique values
    result = conn.execute(text('SELECT COUNT(*) FROM source_records WHERE raw_nace IS NOT NULL')).scalar()
    print(f'\nTotal records with raw_nace: {result}')
    
    result = conn.execute(text('SELECT COUNT(DISTINCT raw_nace) FROM source_records WHERE raw_nace IS NOT NULL')).scalar()
    print(f'Unique raw_nace values: {result}')