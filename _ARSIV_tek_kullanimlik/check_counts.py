from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    ostim_id = '0a27baf8-6dfa-4e57-851b-412470f480e7'
    
    # Count records with kaynak=aso.org.tr in OSTIM source
    rows = conn.execute(text("""
        SELECT COUNT(*)
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload->>'kaynak' = 'aso.org.tr'
    """), {"sid": ostim_id}).fetchone()
    print(f"Records with kaynak=aso.org.tr in OSTIM: {rows[0]}")
    
    # Total records in OSTIM
    rows = conn.execute(text("""
        SELECT COUNT(*)
        FROM source_records sr
        WHERE sr.source_id = :sid
    """), {"sid": ostim_id}).fetchone()
    print(f"Total OSTIM records: {rows[0]}")
    
    # Records with kaynak=ostim.org.tr
    rows = conn.execute(text("""
        SELECT COUNT(*)
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload->>'kaynak' = 'ostim.org.tr'
    """), {"sid": ostim_id}).fetchone()
    print(f"Records with kaynak=ostim.org.tr: {rows[0]}")
    
    # Records with kaynak=NULL
    rows = conn.execute(text("""
        SELECT COUNT(*)
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload->>'kaynak' IS NULL
    """), {"sid": ostim_id}).fetchone()
    print(f"Records with kaynak=NULL: {rows[0]}")