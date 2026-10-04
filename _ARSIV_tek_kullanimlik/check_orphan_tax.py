from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check if orphans have corresponding companies
    # Check by raw_tax_number
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.raw_tax_number
        FROM source_records sr
        WHERE sr.company_id IS NULL
          AND sr.raw_tax_number IS NOT NULL
          AND sr.raw_tax_number != ''
        LIMIT 20
    """)).fetchall()
    print("Orphans with tax number:")
    for r in rows:
        # Check if company exists with this tax
        company = conn.execute(text("SELECT company_id, legal_name FROM companies WHERE tax_number = :tax"), {"tax": r[2]}).fetchone()
        if company:
            print(f"  FOUND: {r[0]} | {r[1][:50]} | tax={r[2]} -> {company[0]} | {company[1]}")
        else:
            print(f"  NOT FOUND: {r[0]} | {r[1][:50]} | tax={r[2]}")
    
    # Check total with tax numbers
    total_with_tax = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE company_id IS NULL AND raw_tax_number IS NOT NULL AND raw_tax_number != ''")).scalar()
    print(f"\nTotal orphans with tax: {total_with_tax}")
    
    # Check companies tax numbers
    company_tax = conn.execute(text("SELECT COUNT(*) FROM companies WHERE tax_number IS NOT NULL AND tax_number != ''")).scalar()
    print(f"Companies with tax: {company_tax}")