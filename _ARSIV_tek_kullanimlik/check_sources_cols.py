from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check sources table columns
    cols = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'sources'
        ORDER BY ordinal_position
    """)).fetchall()
    print("Sources columns:")
    for c in cols:
        print(f"  {c[0]}: {c[1]}")
    
    # Check sources data
    rows = conn.execute(text("SELECT * FROM sources")).fetchall()
    print("\nSources data:")
    for r in rows:
        print(f"  {r}")