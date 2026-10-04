from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check sources table columns
    cols = conn.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'sources'
    """)).fetchall()
    print("Sources columns:")
    for c in cols:
        print(f"  {c[0]}")
    
    # Check orphans by source using correct column
    rows = conn.execute(text("""
        SELECT s.identifier, COUNT(*) as cnt
        FROM source_records sr
        JOIN sources s ON sr.source_id = s.source_id
        WHERE sr.company_id IS NULL
        GROUP BY s.identifier
        ORDER BY cnt DESC
    """)).fetchall()
    print("\nOrphans by source:")
    for r in rows:
        print(f"  {r[0]}: {r[1]}")