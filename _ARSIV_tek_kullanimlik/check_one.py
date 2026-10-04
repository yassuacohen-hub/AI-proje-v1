from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check actual bytes for one record
    rows = conn.execute(text("""
        SELECT source_record_id, raw_name, encode(raw_name::bytea, 'hex') as hex_name
        FROM source_records
        WHERE source_record_id = '6b82f56e-e230-4504-923f-4f1cec8fdca6'
    """)).fetchall()
    for r in rows:
        print(f"  {r[0]} | {r[1]} | {r[2]}")