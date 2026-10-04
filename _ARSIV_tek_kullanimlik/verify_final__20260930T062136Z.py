from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    ostim_id = '0a27baf8-6dfa-4e57-851b-412470f480e7'
    rows = conn.execute(text("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN raw_payload->>'kaynak' IS NULL THEN 1 END) as null_count,
            COUNT(CASE WHEN raw_payload->>'kaynak' = 'ostim.org.tr' THEN 1 END) as ostim_count,
            COUNT(CASE WHEN raw_payload->>'kaynak' = 'aso.org.tr' THEN 1 END) as aso_count
        FROM source_records
        WHERE source_id = :sid
    """), {"sid": ostim_id}).fetchone()
    print(f"Total: {rows[0]}, NULL: {rows[1]}, ostim.org.tr: {rows[2]}, aso.org.tr: {rows[3]}")