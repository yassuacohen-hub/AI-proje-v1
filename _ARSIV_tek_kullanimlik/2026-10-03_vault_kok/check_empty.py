import sys
sys.path.insert(0, 'src')
from company_master.db.connection import get_engine
from sqlalchemy import text
engine = get_engine()
with engine.connect() as conn:
    r = conn.execute(text("SELECT nace_code, level FROM nace_codes WHERE title IS NULL OR title = '' LIMIT 20"))
    for row in r:
        print(f'{row[0]} | level={row[1]}')
    r = conn.execute(text("SELECT COUNT(*) FROM nace_codes WHERE title IS NULL OR title = ''"))
    print(f'Total empty: {r.scalar()}')