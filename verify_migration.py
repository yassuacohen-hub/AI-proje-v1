from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'source_records' AND column_name = 'company_id'")).fetchall()
    print('company_id column:', cols)
    idx = conn.execute(text("SELECT indexname FROM pg_indexes WHERE indexname = 'idx_source_records_company_id'")).fetchall()
    print('Index:', idx)