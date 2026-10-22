import sys
sys.path.insert(0, 'Huginn Data Insights')
from src.company_master.db import get_engine
from sqlalchemy import text

engine = get_engine()

with engine.connect() as conn:
    # Check schema_migrations table structure
    result = conn.execute(text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'schema_migrations'
    """))
    for row in result:
        print(row[0])
    
    # Then query data
    result = conn.execute(text('SELECT * FROM schema_migrations ORDER BY 1'))
    for row in result:
        print(row)