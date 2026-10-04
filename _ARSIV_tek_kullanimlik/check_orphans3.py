from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check orphans by source using correct column
    rows = conn.execute(text("""
        SELECT s.source_name, COUNT(*) as cnt
        FROM source_records sr
        JOIN sources s ON sr.source_id = s.source_id
        WHERE sr.company_id IS NULL
        GROUP BY s.source_name
        ORDER BY cnt DESC
    """)).fetchall()
    print("Orphans by source:")
    for r in rows:
        print(f"  {r[0]}: {r[1]}")