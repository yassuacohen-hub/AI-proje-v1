from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check if the data has actual U+FFFD characters
    rows = conn.execute(text("""
        SELECT source_record_id, raw_name, encode(raw_name::bytea, 'hex') as hex_name
        FROM source_records
        WHERE source_record_id = '6b82f56e-e230-4504-923f-4f1cec8fdca6'
    """)).fetchall()
    for r in rows:
        print(f"Display: {r[1]}")
        print(f"Hex: {r[2]}")
        # Check for U+FFFD (EF BF BD in UTF-8)
        if 'efbfbd' in r[2].lower():
            print("  -> CONTAINS U+FFFD!")
        else:
            print("  -> No U+FFFD")