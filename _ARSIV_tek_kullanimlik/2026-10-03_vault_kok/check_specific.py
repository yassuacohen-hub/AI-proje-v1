import sys
sys.path.insert(0, 'src')
from company_master.db.connection import get_engine
from sqlalchemy import text
engine = get_engine()
with engine.connect() as conn:
    r = conn.execute(text("SELECT nace_code, title FROM nace_codes WHERE nace_code IN ('47.78', '28.15')"))
    for row in r:
        print(f'{row[0]}: {repr(row[1])}')