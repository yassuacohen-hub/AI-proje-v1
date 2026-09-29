import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    # Drop old constraint and add new one with 'invalid_cleared'
    conn.execute(text("ALTER TABLE companies DROP CONSTRAINT companies_nace_source_check"))
    conn.execute(text("""
        ALTER TABLE companies 
        ADD CONSTRAINT companies_nace_source_check 
        CHECK (nace_source = ANY (ARRAY['mersis', 'external', 'predicted', 'sector_default', 'title_default', 'fallback', 'unknown', 'invalid_cleared']))
    """))
    conn.commit()
    print('Check constraint updated successfully')