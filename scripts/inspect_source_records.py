import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()

with engine.connect() as conn:
    # Check sources
    src_result = conn.execute(text('SELECT source_id, source_name, source_type FROM sources ORDER BY source_name'))
    print("Sources:")
    for r in src_result:
        print(f"  {r[0]}: {r[1]} ({r[2]})")
    
    # Check source_records sample
    result = conn.execute(text('''
        SELECT sr.source_record_id, sr.source_id, sr.raw_payload, sr.raw_address, sr.raw_phone, sr.raw_email, sr.raw_website
        FROM source_records sr
        LIMIT 3
    '''))
    print("\nSample source_records:")
    for row in result:
        import json
        payload = row[2] if row[2] else {}
        print(f"  ID: {row[0]}")
        print(f"  source_id: {row[1]}")
        print(f"  raw_address: {row[3]}")
        print(f"  raw_phone: {row[4]}")
        print(f"  raw_email: {row[5]}")
        print(f"  raw_website: {row[6]}")
        print(f"  raw_payload keys: {list(payload.keys()) if isinstance(payload, dict) else type(payload)}")
        print()