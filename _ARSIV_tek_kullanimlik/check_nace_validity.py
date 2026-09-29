from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT company_id, legal_name, nace_code, nace_validity
        FROM companies
        WHERE nace_validity ~ '^[0-9]{2}\.[0-9]{2}'
        ORDER BY company_id
    """)).fetchall()
    print(f'Found {len(rows)} rows with NACE code pattern in nace_validity')
    for r in rows:
        print(f'  {r[0]} | {r[1][:40]} | nace_code={r[2]} | nace_validity={r[3]}')