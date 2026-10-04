from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    ostim_id = '0a27baf8-6dfa-4e57-851b-412470f480e7'
    
    # Check for records that have ASO-like fields in payload
    # ASO records have: naceKod, meslekGrubu, ticaretSicilNo
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.raw_payload
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload ? 'naceKod'
          AND sr.raw_payload->>'kaynak' IS NULL
    """), {"sid": ostim_id}).fetchall()
    print(f"Records with naceKod AND kaynak=None: {len(rows)}")
    for r in rows[:20]:
        print(f"  {r[0]} | {r[1][:50]} | payload={r[2]}")
    
    # Also check for meslekGrubu
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.raw_payload
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload ? 'meslekGrubu'
          AND sr.raw_payload->>'kaynak' IS NULL
    """), {"sid": ostim_id}).fetchall()
    print(f"\nRecords with meslekGrubu AND kaynak=None: {len(rows)}")
    for r in rows[:20]:
        print(f"  {r[0]} | {r[1][:50]} | payload={r[2]}")