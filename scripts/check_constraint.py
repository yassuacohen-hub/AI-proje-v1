import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
with engine.connect() as conn:
    # Check the constraint definition
    result = conn.execute(text("""
        SELECT pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE conname = 'companies_nace_source_check'
    """)).scalar()
    print(f"Constraint: {result}")

    # Check what nace_source values exist in companies
    result = conn.execute(text(
        "SELECT nace_source, COUNT(*) FROM companies WHERE nace_source IS NOT NULL GROUP BY nace_source"
    )).fetchall()
    print(f"nace_source values in companies: {result}")

    # Check what nace_source values are in raw_payload
    result = conn.execute(text("""
        SELECT raw_payload->>'nace_source' as src, COUNT(*)
        FROM source_records
        WHERE raw_payload ? 'nace_source'
        GROUP BY raw_payload->>'nace_source'
    """)).fetchall()
    print(f"raw_payload nace_source values: {result}")

    # Check vergi_no_extracted in payload
    result = conn.execute(text("""
        SELECT COUNT(*) FROM source_records
        WHERE raw_payload ? 'vergi_no_extracted'
          AND raw_payload->>'vergi_no_extracted' IS NOT NULL
          AND raw_payload->>'vergi_no_extracted' != ''
    """)).scalar()
    print(f"vergi_no_extracted not-null: {result}")

    # Check osb_parsel_extracted
    result = conn.execute(text("""
        SELECT COUNT(*) FROM source_records
        WHERE raw_payload ? 'osb_parsel_extracted'
          AND raw_payload->>'osb_parsel_extracted' IS NOT NULL
          AND raw_payload->>'osb_parsel_extracted' != ''
    """)).scalar()
    print(f"osb_parsel_extracted not-null: {result}")

    # Check vergi_no in payload
    result = conn.execute(text("""
        SELECT COUNT(*) FROM source_records
        WHERE raw_payload ? 'vergi_no'
          AND raw_payload->>'vergi_no' IS NOT NULL
          AND raw_payload->>'vergi_no' != ''
    """)).scalar()
    print(f"vergi_no (direct) not-null: {result}")