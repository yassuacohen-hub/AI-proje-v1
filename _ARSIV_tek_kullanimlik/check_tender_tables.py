from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check for tender-related tables
    tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND (table_name LIKE '%tender%' OR table_name LIKE '%ihale%')")).fetchall()
    print('Tender/ihale tables:', tables)
    # Check for source list
    sources = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND (table_name LIKE '%source%' OR table_name LIKE '%osb%')")).fetchall()
    print('Source/OSB tables:', sources)