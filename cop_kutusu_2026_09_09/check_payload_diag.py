import sys
sys.path.insert(0, 'src')
from company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    r = conn.execute(text('SELECT COUNT(*) FROM source_records sr JOIN companies c ON c.source_record_id = sr.source_record_id')).scalar()
    print(f'Joined records: {r}')
    r2 = conn.execute(text('SELECT COUNT(*) FROM source_records')).scalar()
    print(f'Total source_records: {r2}')
    r3 = conn.execute(text('SELECT COUNT(*) FROM companies')).scalar()
    print(f'Total companies: {r3}')
    r4 = conn.execute(text('SELECT COUNT(*) FROM companies WHERE source_record_id IS NULL')).scalar()
    print(f'Companies without source_record_id: {r4}')
    r5 = conn.execute(text("SELECT raw_payload->>'adres' FROM source_records WHERE raw_payload->>'adres' IS NOT NULL LIMIT 5")).fetchall()
    print(f'Sample adres values from payload: {r5}')
    r6 = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE raw_payload->>'adres' IS NOT NULL")).scalar()
    print(f'Source records with adres in payload: {r6}')
