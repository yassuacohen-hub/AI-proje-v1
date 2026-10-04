from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check if companies also have mojibake
    rows = conn.execute(text("""
        SELECT company_id, legal_name
        FROM companies
        WHERE legal_name LIKE '%�%'
        LIMIT 20
    """)).fetchall()
    print("Companies with mojibake:")
    for r in rows:
        print(f"  {r[0]} | {r[1]}")