from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    for code in ['98', '71', '16', '78']:
        r = conn.execute(text(f"SELECT nace_code FROM nace_codes WHERE nace_code = '{code}'")).fetchone()
        print(f'{code} in nace_codes: {r}')