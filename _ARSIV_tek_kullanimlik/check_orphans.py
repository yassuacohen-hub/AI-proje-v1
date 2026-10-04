from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check source_records count
    total = conn.execute(text("SELECT COUNT(*) FROM source_records")).scalar()
    print(f"Total source_records: {total}")
    
    # Check orphans (company_id NULL)
    orphans = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE company_id IS NULL")).scalar()
    print(f"Orphans (company_id=NULL): {orphans}")
    
    # Check orphans by source
    rows = conn.execute(text("""
        SELECT s.name, COUNT(*) as cnt
        FROM source_records sr
        JOIN sources s ON sr.source_id = s.source_id
        WHERE sr.company_id IS NULL
        GROUP BY s.name
        ORDER BY cnt DESC
    """)).fetchall()
    print("\nOrphans by source:")
    for r in rows:
        print(f"  {r[0]}: {r[1]}")