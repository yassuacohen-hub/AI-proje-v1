from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Update title_default to medium (they have valid nace_codes)
    result = conn.execute(text("""
        UPDATE companies
        SET nace_validity = 'medium'
        WHERE nace_validity = 'title_default'
    """))
    print(f'Updated {result.rowcount} rows from title_default to medium')
    conn.commit()
    
    # Verify
    rows = conn.execute(text("""
        SELECT nace_validity, COUNT(*) as cnt
        FROM companies
        GROUP BY nace_validity
        ORDER BY cnt DESC
    """)).fetchall()
    print('\nAfter fix:')
    for r in rows:
        print(f'  {r[0]}: {r[1]}')