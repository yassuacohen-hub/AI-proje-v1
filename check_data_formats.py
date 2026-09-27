from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # Check companies legal_name samples
    print("=== Companies legal_name samples ===")
    rows = conn.execute(text("SELECT legal_name FROM companies LIMIT 10")).fetchall()
    for r in rows:
        print(f"  '{r[0]}'")
    
    print("\n=== Source_records raw_name samples ===")
    rows = conn.execute(text("SELECT raw_name FROM source_records WHERE company_id IS NULL LIMIT 10")).fetchall()
    for r in rows:
        print(f"  '{r[0]}'")
    
    # Check raw_tax_number
    print("\n=== Source_records raw_tax_number samples ===")
    rows = conn.execute(text("SELECT raw_tax_number FROM source_records WHERE company_id IS NULL AND raw_tax_number IS NOT NULL LIMIT 10")).fetchall()
    for r in rows:
        print(f"  '{r[0]}'")
    
    print("\n=== Companies tax_number samples ===")
    rows = conn.execute(text("SELECT tax_number FROM companies WHERE tax_number IS NOT NULL LIMIT 10")).fetchall()
    for r in rows:
        print(f"  '{r[0]}'")