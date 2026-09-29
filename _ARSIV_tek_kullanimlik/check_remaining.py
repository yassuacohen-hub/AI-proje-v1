from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # Check NN.NN codes not in nace_codes
    rows = conn.execute(text("""
        SELECT c.nace_code, COUNT(*) as cnt
        FROM companies c
        LEFT JOIN nace_codes nc ON c.nace_code = nc.nace_code
        WHERE c.nace_code ~ '^[0-9]{2}\\.[0-9]{2}$'
        AND nc.nace_code IS NULL
        GROUP BY c.nace_code
        ORDER BY cnt DESC
    """)).fetchall()
    print('NN.NN codes NOT in nace_codes:')
    for r in rows:
        print(f'  {r[0]}: {r[1]}')
    
    # Check 2-digit codes
    rows = conn.execute(text("""
        SELECT nace_code, COUNT(*) as cnt
        FROM companies
        WHERE nace_code ~ '^[0-9]{2}$'
        GROUP BY nace_code
        ORDER BY cnt DESC
    """)).fetchall()
    print('2-digit codes:')
    for r in rows:
        print(f'  {r[0]}: {r[1]}')