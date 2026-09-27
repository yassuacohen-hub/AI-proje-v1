from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # Count NN.NN format total
    total = conn.execute(text("""
        SELECT COUNT(*) FROM companies
        WHERE nace_code ~ '^[0-9]{2}\\.[0-9]{2}$'
    """)).scalar()
    print(f'NN.NN format total: {total}')
    
    # Count 6-digit
    total6 = conn.execute(text("""
        SELECT COUNT(*) FROM companies
        WHERE nace_code ~ '^[0-9]{2}\\.[0-9]{2}\\.[0-9]{2}$'
    """)).scalar()
    print(f'6-digit total: {total6}')
    
    # Count 2-digit
    total2 = conn.execute(text("""
        SELECT COUNT(*) FROM companies
        WHERE nace_code ~ '^[0-9]{2}$'
    """)).scalar()
    print(f'2-digit total: {total2}')
    
    # Check specific codes mentioned in brief
    for code in ['10.11', '29.10', '62.09', '62.01', '41.10']:
        cnt = conn.execute(text(f"SELECT COUNT(*) FROM companies WHERE nace_code = '{code}'")).scalar()
        print(f'{code}: {cnt}')