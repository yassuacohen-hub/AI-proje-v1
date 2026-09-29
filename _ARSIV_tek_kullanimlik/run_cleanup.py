from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with open('cleanup_hayalet.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

print('SQL çalıştırılıyor...')
with engine.begin() as conn:
    conn.execute(text(sql))
    print('Tamamlandı!')

# Doğrula
with engine.connect() as conn:
    total, distinct = conn.execute(text('SELECT count(*), count(distinct legal_name) FROM companies')).fetchone()
    print(f'Toplam: {total}, Distinct legal_name: {distinct}')
    idx = conn.execute(text("SELECT indexname FROM pg_indexes WHERE indexname = 'uq_companies_legal_name'")).fetchone()
    print(f'UNIQUE INDEX: {idx}')