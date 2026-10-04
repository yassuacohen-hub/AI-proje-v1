from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    ostim_id = '0a27baf8-6dfa-4e57-851b-412470f480e7'
    
    # Update all records with kaynak=NULL in OSTIM source to have kaynak=ostim.org.tr
    result = conn.execute(text("""
        UPDATE source_records
        SET raw_payload = jsonb_set(raw_payload, '{kaynak}', '"ostim.org.tr"')
        WHERE source_id = :sid
          AND raw_payload->>'kaynak' IS NULL
    """), {"sid": ostim_id})
    print(f"Updated {result.rowcount} records from kaynak=NULL to ostim.org.tr")
    conn.commit()
    
    # Verify
    rows = conn.execute(text("""
        SELECT COUNT(*)
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload->>'kaynak' IS NULL
    """), {"sid": ostim_id}).fetchone()
    print(f"Remaining with kaynak=NULL: {rows[0]}")
    
    rows = conn.execute(text("""
        SELECT COUNT(*)
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload->>'kaynak' = 'ostim.org.tr'
    """), {"sid": ostim_id}).fetchone()
    print(f"Now with kaynak=ostim.org.tr: {rows[0]}")