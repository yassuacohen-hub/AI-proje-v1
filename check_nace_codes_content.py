from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # Check if 10.11 and 29.10 are in nace_codes
    for code in ['10.11', '29.10', '10.11.00', '29.10.00']:
        r = conn.execute(text(f"SELECT nace_code FROM nace_codes WHERE nace_code = '{code}'")).fetchone()
        print(f'{code}: {r}')
    
    # Check NN.NN format in nace_codes
    rows = conn.execute(text("""
        SELECT nace_code FROM nace_codes
        WHERE nace_code ~ '^[0-9]{2}\\.[0-9]{2}$'
        ORDER BY nace_code
    """)).fetchall()
    print(f'NN.NN in nace_codes: {len(rows)}')
    for r in rows[:20]:
        print(f'  {r[0]}')