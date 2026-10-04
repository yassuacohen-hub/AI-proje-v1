from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check source_records with source=None or empty
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.source_id, sr.source
        FROM source_records sr
        WHERE sr.source IS NULL OR sr.source = ''
    """)).fetchall()
    print(f"Total source=None records: {len(rows)}")
    
    # Check specifically OSTIM related
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.source_id, sr.source
        FROM source_records sr
        WHERE (sr.source IS NULL OR sr.source = '')
          AND sr.raw_name ILIKE '%ostim%'
    """)).fetchall()
    print(f"OSTIM related source=None: {len(rows)}")
    for r in rows[:10]:
        print(f"  {r[0]} | {r[1][:50]} | source_id={r[2]} | source={r[3]}")