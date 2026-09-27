import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    
    # Invalid codes to clean (all have nace_source='unknown')
    invalid_codes = ['1163', '410', '780', '794', '757', '110', '114', '127', '192', '339', '380', '390', '410', '752', '757', '780', '794', '757', '339', '410']
    
    # Remove duplicates
    invalid_codes = list(set(invalid_codes))
    print(f'Invalid codes to clean: {len(invalid_codes)}')
    for code in sorted(invalid_codes):
        print(f'  {code}')
    
    # First, get the count of affected companies
    placeholders = ','.join([f':code{i}' for i in range(len(invalid_codes))])
    params = {f'code{i}': code for i, code in enumerate(invalid_codes)}
    
    # Count affected companies
    query = f'''
        SELECT nace_code, COUNT(*) as cnt
        FROM companies 
        WHERE nace_code IN ({','.join([f':code{i}' for i in range(len(invalid_codes))])})
        GROUP BY nace_code
        ORDER BY cnt DESC
    '''
    result = conn.execute(text(f'''
        SELECT nace_code, COUNT(*) as cnt
        FROM companies 
        WHERE nace_code IN ({','.join([f':code{i}' for i in range(len(invalid_codes))])})
        GROUP BY nace_code
        ORDER BY cnt DESC
    '''), {f'code{i}': code for i, code in enumerate(invalid_codes)}).fetchall()
    
    print('Affected companies per code:')
    total_affected = 0
    for row in conn.execute(text(f'''
        SELECT nace_code, COUNT(*) as cnt
        FROM companies 
        WHERE nace_code IN ({','.join([f':code{i}' for i in range(len(invalid_codes))])})
        GROUP BY nace_code
        ORDER BY cnt DESC
    '''), {f'code{i}': code for i, code in enumerate(invalid_codes)}).fetchall():
        print(f'  {row[0]}: {row[1]} firma')
        total_affected += row[1]
    
    print(f'\nTotal affected companies: {sum(row[1] for row in result)}')
    
    # Confirm before proceeding
    confirm = input('\nBu kayıtları temizlemek istiyor musunuz? (evet/hayır): ')
    if confirm.lower() != 'evet':
        print('[IPTAL] İşlem iptal edildi.')
        exit()
    
    # Perform cleanup
    print('\n[İŞLEM] Temizleme başlıyor...')
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
    print(f'\n[SONUÇ] Temizlenen firma sayısı: {affected_count}')
    
    # Verify cleanup
    from sqlalchemy import text
    result = conn.execute(text("SELECT COUNT(*) FROM companies WHERE nace_code IS NOT NULL AND nace_code NOT IN (SELECT nace_code FROM nace_codes)")).scalar()
    print(f'[DOĞRULAMA] Kalan geçersiz NACE kodları: {result}')
    
    result = conn.execute(text("SELECT COUNT(*) FROM companies WHERE nace_source = 'invalid_cleared'")).scalar()
    print(f'[DOĞRULAMA] invalid_cleared işaretli firma sayısı: {result}')
    
    # Verify company count unchanged
    result = conn.execute(text('SELECT COUNT(*) FROM companies')).scalar()
    print(f'[DOĞRULAMA] Toplam firma sayısı (değişmemeli): {result}')