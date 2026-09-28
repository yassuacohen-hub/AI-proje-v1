from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # For the 21 title_default rows, check their nace_code and determine correct validity
    rows = conn.execute(text("""
        SELECT company_id, legal_name, nace_code, nace_validity
        FROM companies
        WHERE nace_validity = 'title_default'
    """)).fetchall()
    print(f'Found {len(rows)} rows with title_default')
    for r in rows:
        print(f'  {r[0]} | {r[1][:40]} | nace_code={r[2]} | nace_validity={r[3]}')
    
    # Check valid nace_codes to determine validity
    print('\n--- Checking if nace_code exists in nace_codes ---')
    for r in rows:
        cid = r[0]
        nace = r[2]
        if nace:
            exists = conn.execute(text("SELECT 1 FROM nace_codes WHERE nace_code = :nace"), {"nace": nace}).scalar()
            print(f'  {cid} | nace_code={nace} | in nace_codes={bool(exists)}')
        else:
            print(f'  {cid} | nace_code=NULL')