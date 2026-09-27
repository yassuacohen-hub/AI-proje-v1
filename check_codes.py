from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    r = conn.execute(text("SELECT nace_code, title, level FROM nace_codes WHERE nace_code='47.79'")).fetchone()
    print('47.79:', r)
    r = conn.execute(text("SELECT nace_code, title, level FROM nace_codes WHERE nace_code='47.79.04'")).fetchone()
    print('47.79.04:', r)
    for code in ['29.10', '62.01', '41.10', '29.10.01', '62.09']:
        r = conn.execute(text(f"SELECT nace_code, title, level FROM nace_codes WHERE nace_code='{code}'")).fetchone()
        print(f'{code}:', r)
    orphan = conn.execute(text("SELECT count(*) FROM nace_codes WHERE parent_code IS NOT NULL AND parent_code NOT IN (SELECT nace_code FROM nace_codes)")).scalar()
    print('Orphan:', orphan)