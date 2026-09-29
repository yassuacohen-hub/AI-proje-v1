from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check for any non-standard values in nace_validity
    rows = conn.execute(text("""
        SELECT company_id, legal_name, nace_code, nace_validity
        FROM companies
        WHERE nace_validity IS NOT NULL
          AND nace_validity NOT IN ('unknown', 'medium', 'fallback')
        ORDER BY company_id
    """)).fetchall()
    print(f'Found {len(rows)} rows with unexpected nace_validity values')
    for r in rows:
        print(f'  {r[0]} | {r[1][:40]} | nace_code={r[2]} | nace_validity={r[3]}')