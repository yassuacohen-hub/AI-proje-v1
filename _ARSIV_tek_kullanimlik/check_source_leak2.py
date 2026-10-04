from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check source_records columns
    cols = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'source_records'
        ORDER BY ordinal_position
    """)).fetchall()
    print("source_records columns:")
    for c in cols:
        print(f"  {c[0]}: {c[1]}")
    
    # Check source_records with source_id NULL
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.source_id
        FROM source_records sr
        WHERE sr.source_id IS NULL
    """)).fetchall()
    print(f"\nTotal source_id=NULL records: {len(rows)}")
    
    # Check specifically OSTIM related
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.source_id
        FROM source_records sr
        WHERE sr.source_id IS NULL
          AND sr.raw_name ILIKE '%ostim%'
    """)).fetchall()
    print(f"OSTIM related source_id=NULL: {len(rows)}")
    for r in rows[:20]:
        print(f"  {r[0]} | {r[1][:60]} | source_id={r[2]}")