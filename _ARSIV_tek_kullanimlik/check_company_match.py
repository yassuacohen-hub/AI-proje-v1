from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Search for companies matching the source record
    rows = conn.execute(text("""
        SELECT company_id, legal_name
        FROM companies
        WHERE legal_name ILIKE '%3dtim%'
           OR legal_name ILIKE '%elektronik%'
           OR legal_name ILIKE '%3dt%'
    """)).fetchall()
    print("Companies matching:")
    for r in rows:
        print(f"  {r[0]} | {r[1]}")
    
    # Check all companies with similar names
    rows = conn.execute(text("""
        SELECT company_id, legal_name
        FROM companies
        WHERE legal_name ILIKE '%3DT%'
           OR legal_name ILIKE '%ELEKTRONIK%'
           OR legal_name ILIKE '%A.S.%'
    """)).fetchall()
    print(f"\nTotal companies with similar names: {len(rows)}")
    for r in rows[:20]:
        print(f"  {r[0]} | {r[1]}")