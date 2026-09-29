from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Final verification
    rows = conn.execute(text("""
        SELECT COUNT(*) FROM companies
        WHERE nace_validity ~ '^[0-9]{2}\.[0-9]{2}'
    """)).scalar()
    print(f'Rows with NACE pattern in nace_validity: {rows}')
    
    rows = conn.execute(text("""
        SELECT nace_validity, COUNT(*) as cnt
        FROM companies
        GROUP BY nace_validity
        ORDER BY cnt DESC
    """)).fetchall()
    print('\nFinal nace_validity distribution:')
    for r in rows:
        print(f'  {r[0]}: {r[1]}')