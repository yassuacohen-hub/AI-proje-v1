from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    ostim_id = '0a27baf8-6dfa-4e57-851b-412470f480e7'
    
    # Check for records with 'payload' key containing ASO format
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.raw_payload
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload ? 'payload'
    """), {"sid": ostim_id}).fetchall()
    print(f"Records with 'payload' key: {len(rows)}")
    for r in rows[:10]:
        print(f"  {r[0]} | {r[1][:50]} | payload_keys={list(r[2].keys()) if r[2] else None}")
    
    # Check if ASO fields are in the 'payload' sub-object
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.raw_payload
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload ? 'payload'
          AND sr.raw_payload->'payload' ? 'naceKod'
    """), {"sid": ostim_id}).fetchall()
    print(f"\nRecords with nested payload.naceKod: {len(rows)}")
    for r in rows[:10]:
        print(f"  {r[0]} | {r[1][:50]} | payload.naceKod={r[2].get('payload', {}).get('naceKod')}")
    
    # Check for records with 'naceKod' anywhere in JSON (text search)
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload::text LIKE '%naceKod%'
    """), {"sid": ostim_id}).fetchall()
    print(f"\nRecords with 'naceKod' anywhere in JSON text: {len(rows)}")