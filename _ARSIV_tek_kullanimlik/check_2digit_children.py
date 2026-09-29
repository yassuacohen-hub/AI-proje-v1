from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    for code in ['98', '71', '16', '78']:
        rows = conn.execute(text(f"""
            SELECT nace_code FROM nace_codes
            WHERE nace_code LIKE '{code}.%'
            ORDER BY nace_code
        """)).fetchall()
        print(f'{code} children ({len(rows)}):')
        for r in rows[:20]:
            print(f'  {r[0]}')
        if len(rows) > 20:
            print(f'  ... and {len(rows)-20} more')
        print()