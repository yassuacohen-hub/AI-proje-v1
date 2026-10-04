from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    ostim_id = '0a27baf8-6dfa-4e57-851b-412470f480e7'
    
    # Check for 'kaynak' key presence vs value
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name,
               sr.raw_payload ? 'kaynak' as has_key,
               sr.raw_payload->>'kaynak' as kaynak_value
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload ? 'naceKod'
    """), {"sid": ostim_id}).fetchall()
    print(f"Records with naceKod (any kaynak): {len(rows)}")
    for r in rows:
        print(f"  {r[0]} | {r[1][:50]} | has_key={r[2]} | value={r[3]}")
    
    # Also check for records with meslekGrubu or ticaretSicilNo
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name,
               sr.raw_payload ? 'meslekGrubu' as has_meslek,
               sr.raw_payload ? 'ticaretSicilNo' as has_ticaret
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload->>'kaynak' IS NULL
    """), {"sid": ostim_id}).fetchall()
    print(f"\nRecords with kaynak=NULL: {len(rows)}")
    for r in rows[:20]:
        print(f"  {r[0]} | {r[1][:50]} | meslek={r[2]} | ticaret={r[3]}")