from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check actual bytes
    rows = conn.execute(text("""
        SELECT source_record_id, encode(raw_name::bytea, 'hex') as hex_name
        FROM source_records
        LIMIT 10
    """)).fetchall()
    for r in rows:
        print(f"  {r[0]} | {r[1]}")