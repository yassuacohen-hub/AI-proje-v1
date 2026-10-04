from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    ostim_id = '0a27baf8-6dfa-4e57-851b-412470f480e7'
    
    # Check raw_payload structure
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.raw_payload
        FROM source_records sr
        WHERE sr.source_id = :sid
        LIMIT 10
    """), {"sid": ostim_id}).fetchall()
    print("Sample raw_payloads:")
    for r in rows:
        print(f"  {r[0]} | {r[1][:50]} | {r[2]}")
    
    # Check company_id NULL - these are the ones that need source linking
    # The task says "kaynak=None" - maybe source_id is not the issue, but the company linkage
    # Let's check if the 833 records with company_id=NULL need to be linked
    
    # Check the 102 ASO records - maybe they're in ASO source (aso.org.tr)
    aso_id = '534bc9d8-6faa-4fde-a60d-626eb4ff65df'
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.company_id, sr.raw_payload
        FROM source_records sr
        WHERE sr.source_id = :sid
        LIMIT 20
    """), {"sid": aso_id}).fetchall()
    print(f"ASO source records: {len(rows)}")
    for r in rows:
        print(f"  {r[0]} | {r[1][:50]} | company_id={r[2]} | payload={r[3]}")
    
    # Check company_id NULL in ASO
    rows_null = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name
        FROM source_records sr
        WHERE sr.source_id = :sid AND sr.company_id IS NULL
    """), {"sid": aso_id}).fetchall()
    print(f"ASO records with company_id=NULL: {len(rows_null)}")