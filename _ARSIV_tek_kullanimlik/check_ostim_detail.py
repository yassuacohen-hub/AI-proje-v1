from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    ostim_id = '0a27baf8-6dfa-4e57-851b-412470f480e7'
    
    # Check records with OSTIM source_id
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.source_id, sr.company_id, sr.raw_payload
        FROM source_records sr
        WHERE sr.source_id = :sid
    """), {"sid": ostim_id}).fetchall()
    print(f"Records with OSTIM source_id: {len(rows)}")
    
    # Check company_id NULL
    rows_null = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.company_id, sr.raw_payload
        FROM source_records sr
        WHERE sr.source_id = :sid AND sr.company_id IS NULL
    """), {"sid": ostim_id}).fetchall()
    print(f"OSTIM records with company_id=NULL: {len(rows_null)}")
    
    # Check ASO type in raw_payload
    aso_rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.raw_payload
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload->>'type' = 'ASO'
    """), {"sid": ostim_id}).fetchall()
    print(f"ASO type records: {len(aso_rows)}")
    for r in aso_rows[:10]:
        print(f"  {r[0]} | {r[1][:60]} | payload={r[2]}")
    
    # Check all distinct types in payload
    types = conn.execute(text("""
        SELECT DISTINCT sr.raw_payload->>'type' as type, COUNT(*)
        FROM source_records sr
        WHERE sr.source_id = :sid
        GROUP BY sr.raw_payload->>'type'
        ORDER BY COUNT(*) DESC
    """), {"sid": ostim_id}).fetchall()
    print("\nPayload types:")
    for t in types:
        print(f"  {t[0]}: {t[1]}")