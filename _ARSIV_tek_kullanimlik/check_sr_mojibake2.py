from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check raw bytes for mojibake patterns
    rows = conn.execute(text("""
        SELECT source_record_id, raw_name
        FROM source_records
        WHERE raw_name ~ '[ĐÝÅÃÄ]'
        LIMIT 10
    """)).fetchall()
    print(f"Records with mojibake patterns: {len(rows)}")
    for r in rows:
        print(f"  {r[0]} | {r[1]}")