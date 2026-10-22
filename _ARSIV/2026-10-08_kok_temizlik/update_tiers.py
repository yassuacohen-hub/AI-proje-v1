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
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    # Update terminal -> Temel
    result = conn.execute(text('UPDATE users SET tier = :new WHERE tier = :old'), {'new': 'Temel', 'old': 'terminal'})
    print(f'Updated {result.rowcount} rows from terminal to Temel')
    # Update enterprise -> Kurumsal
    result = conn.execute(text('UPDATE users SET tier = :new WHERE tier = :old'), {'new': 'Kurumsal', 'old': 'enterprise'})
    print(f'Updated {result.rowcount} rows from enterprise to Kurumsal')
    # Verify
    result = conn.execute(text('SELECT DISTINCT tier FROM users'))
    tiers = [row[0] for row in result]
    print('Distinct tier values after update:', tiers)
    for t in tiers:
        cnt = conn.execute(text('SELECT COUNT(*) FROM users WHERE tier = :tier'), {'tier': t}).scalar()
        print(f'  {t}: {cnt}')
