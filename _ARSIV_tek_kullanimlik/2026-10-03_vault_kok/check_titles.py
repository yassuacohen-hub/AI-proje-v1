import sys
sys.path.insert(0, 'src')
from company_master.db.connection import get_engine
from sqlalchemy import text
engine = get_engine()
with engine.connect() as conn:
    r = conn.execute(text("SELECT COUNT(*) FROM nace_codes WHERE title IS NULL OR title = ''"))
    print('Empty titles:', r.scalar())
    r = conn.execute(text("SELECT COUNT(*) FROM nace_codes WHERE title IS NOT NULL AND title != ''"))
    print('Non-empty titles:', r.scalar())
    r = conn.execute(text("SELECT COUNT(*) FROM nace_codes"))
    print('Total:', r.scalar())