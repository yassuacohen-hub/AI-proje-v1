from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check distribution of nace_validity values
    rows = conn.execute(text("""
        SELECT nace_validity, COUNT(*) as cnt
        FROM companies
        GROUP BY nace_validity
        ORDER BY cnt DESC
    """)).fetchall()
    print('nace_validity value distribution:')
    for r in rows:
        print(f'  {r[0]}: {r[1]}')