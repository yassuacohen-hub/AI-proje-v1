import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

script_dir = Path(__file__).parent
env_path = script_dir / 'Huginn Data Insights' / '.env'
load_dotenv(dotenv_path=env_path)
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError('DATABASE_URL not set')
print('DATABASE_URL found:', DATABASE_URL[:50] + '...')
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    # Distinct tier values and count
    result = conn.execute(text('SELECT DISTINCT tier FROM users'))
    tiers = [row[0] for row in result]
    tier_counts = {}
    for t in tiers:
        cnt = conn.execute(text('SELECT COUNT(*) FROM users WHERE tier = :tier'), {'tier': t}).scalar()
        tier_counts[t] = cnt
    print('Tier counts:', tier_counts)
    # linked_company_id not null count
    linked_cnt = conn.execute(text('SELECT COUNT(*) FROM users WHERE linked_company_id IS NOT NULL')).scalar()
    print('Users with linked_company_id set:', linked_cnt)
    # DEFAULT_TIER_LIMITS from rate_limiter.py? We'll just note we need to check.
    print('Please check rate_limiter.py for DEFAULT_TIER_LIMITS')
