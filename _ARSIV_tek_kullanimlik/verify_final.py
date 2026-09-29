import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    # Final verification
    result = conn.execute(text("SELECT COUNT(*) FROM companies WHERE nace_code IS NOT NULL AND nace_code NOT IN (SELECT nace_code FROM nace_codes)")).scalar()
    print(f'[DOGRULAMA] Kalan gecersiz NACE kodlari: {result}')
    
    result = conn.execute(text("SELECT COUNT(*) FROM companies WHERE nace_source = 'invalid_cleared'")).scalar()
    print(f'[DOGRULAMA] invalid_cleared isaretli firma sayisi: {result}')
    
    result = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
    print(f'Toplam firma sayisi: {result}')
    
    result = conn.execute(text("SELECT nace_source, COUNT(*) FROM companies GROUP BY nace_source ORDER BY COUNT(*) DESC")).fetchall()
    for row in result:
        print(f'{row[0]}: {row[1]}')