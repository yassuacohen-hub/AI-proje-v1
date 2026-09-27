from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check if migration 0022 was applied
    r = conn.execute(text("SELECT indexname FROM pg_indexes WHERE indexname = 'uq_companies_legal_name'")).fetchone()
    print('uq_companies_legal_name index:', r)
    # Check companies count
    r = conn.execute(text("SELECT count(*), count(distinct legal_name) FROM companies")).fetchone()
    print('Companies total / distinct legal_name:', r)
    r = conn.execute(text("SELECT count(*) FROM companies WHERE vergi_no IS NOT NULL AND vergi_no != ''")).scalar()
    print('vergi_no dolu:', r)