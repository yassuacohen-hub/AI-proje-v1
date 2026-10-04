from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    ostim_id = '0a27baf8-6dfa-4e57-851b-412470f480e7'
    
    # Check records where raw_payload->>'kaynak' is null or not 'ostim.org.tr'
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.raw_payload->>'kaynak' as kaynak
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND (sr.raw_payload->>'kaynak' IS NULL OR sr.raw_payload->>'kaynak' = '')
    """), {"sid": ostim_id}).fetchall()
    print(f"Records with kaynak NULL/empty: {len(rows)}")
    for r in rows[:20]:
        print(f"  {r[0]} | {r[1][:50]} | kaynak={r[2]}")
    
    # Check for records with 'kaynak' not equal to 'ostim.org.tr'
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.raw_payload->>'kaynak' as kaynak
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload->>'kaynak' IS NOT NULL
          AND sr.raw_payload->>'kaynak' != 'ostim.org.tr'
    """), {"sid": ostim_id}).fetchall()
    print(f"\nRecords with kaynak != 'ostim.org.tr': {len(rows)}")
    for r in rows[:20]:
        print(f"  {r[0]} | {r[1][:50]} | kaynak={r[2]}")