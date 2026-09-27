from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    for code in ['10.11', '29.10']:
        rows = conn.execute(text(f"""
            SELECT c.company_id, c.legal_name, c.nace_code, nc.title
            FROM companies c
            JOIN nace_codes nc ON c.nace_code = nc.nace_code
            WHERE c.nace_code = '{code}'
            LIMIT 3
        """)).fetchall()
        print(f'{code} firmaları:')
        for r in rows:
            print(f'  {r[0]} | {r[1]} | {r[2]} | {r[3]}')
        print()