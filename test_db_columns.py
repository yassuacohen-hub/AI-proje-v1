import sys
sys.path.insert(0, 'Huginn Data Insights')
from src.company_master.db import get_engine
from sqlalchemy import text

engine = get_engine()
print('Engine:', engine)
print('URL:', engine.url)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'companies'
        ORDER BY column_name
    """))
    cols = [row[0] for row in result]
    for c in cols:
        print(c)