from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check sample raw_name for orphans
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.raw_tax_number
        FROM source_records sr
        WHERE sr.company_id IS NULL
        LIMIT 20
    """)).fetchall()
    print("Sample orphan raw_names:")
    for r in rows:
        print(f"  {r[0]} | {r[1]} | tax={r[2]}")
    
    # Check companies legal_name format
    rows = conn.execute(text("""
        SELECT company_id, legal_name, tax_number
        FROM companies
        LIMIT 20
    """)).fetchall()
    print("\nSample companies:")
    for r in rows:
        print(f"  {r[0]} | {r[1]} | tax={r[2]}")