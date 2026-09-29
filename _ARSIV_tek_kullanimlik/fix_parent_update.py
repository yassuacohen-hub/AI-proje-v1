import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text
engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    # Update parent_code for level 4 records
    result = conn.execute(text('''
        UPDATE nace_codes 
        SET parent_code = LEFT(nace_code, POSITION('.' IN nace_code) - 1)
        WHERE level = 4 
        AND parent_code IS NULL
        AND POSITION('.' IN nace_code) > 0
    ''')
    conn.commit()
    print(f'Updated {result.rowcount} level 4 records with parent_code')
    
    # Verify
    result = conn.execute(text('SELECT DISTINCT parent_code, COUNT(*) as cnt FROM nace_codes WHERE level = 4 GROUP BY parent_code ORDER BY parent_code')).fetchall()
    for row in result:
        print(f'Parent: \"{row[0]}\" Count: {row[1]}')