import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text
from datetime import datetime
from pathlib import Path

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    
    # Invalid codes to clean (all have nace_source='unknown')
    invalid_codes = list(set(['1163', '410', '780', '794', '757', '110', '114', '127', '192', '339', '380', '390', '410', '752', '757', '780', '794', '757', '339', '410']))
    
    print(f'Invalid codes to clean: {len(invalid_codes)}')
    for code in sorted(invalid_codes):
        print(f'  {code}')
    
    # Count affected companies
    placeholders = ','.join([f':code{i}' for i in range(len(invalid_codes))])
    params = {f'code{i}': code for i, code in enumerate(invalid_codes)}
    
    result = conn.execute(text(f'''
        SELECT nace_code, COUNT(*) as cnt
        FROM companies 
        WHERE nace_code IN ({','.join([f':code{i}' for i in range(len(invalid_codes))])})
        GROUP BY nace_code
        ORDER BY cnt DESC
    '''), params).fetchall()
    
    print('Affected companies per code:')
    total_affected = 0
    for row in result:
        print(f'  {row[0]}: {row[1]} firma')
        total_affected += row[1]
    
    print(f'\nTotal affected companies: {total_affected}')
    
    # Perform cleanup - set to NULL and update nace_source
    print('\n[ISLEM] Temizleme basliyor...')
    affected_count = 0
    for code in invalid_codes:
        result = conn.execute(text("""
            UPDATE companies 
            SET nace_code = NULL, nace_source = 'invalid_cleared'
            WHERE nace_code = :code
        """), {"code": code})
        affected = result.rowcount
        if affected > 0:
            affected_count += affected
            print(f'  Temizlendi: {code} ({affected} firma)')
    
    conn.commit()
    print(f'\n[SONUC] Temizlenen firma sayisi: {affected_count}')
    
    # Verify cleanup
    result = conn.execute(text("SELECT COUNT(*) FROM companies WHERE nace_code IS NOT NULL AND nace_code NOT IN (SELECT nace_code FROM nace_codes)")).scalar()
    print(f'[DOGRULAMA] Kalan gecersiz NACE kodlari: {result}')
    
    result = conn.execute(text("SELECT COUNT(*) FROM companies WHERE nace_source = 'invalid_cleared'")).scalar()
    print(f'[DOGRULAMA] invalid_cleared isaretli firma sayisi: {result}')
    
    # Verify company count unchanged
    result = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
    print(f'[DOGRULAMA] Toplam firma sayisi (degismemeli): {result}')