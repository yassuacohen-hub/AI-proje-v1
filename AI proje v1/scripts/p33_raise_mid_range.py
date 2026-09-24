import json, os
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

root = Path(__file__).resolve().parents[1]
load_dotenv(root / '.env')
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url, echo=False, future=True)

DETAYLI = root / 'data/ostim/firmalar_detayli.jsonl'
GENERIC = {'http://www.isim.org.tr', 'http://www.osp.com.tr', 'https://www.ostimonline.com/home/ostimmain'}

records = []
with open(DETAYLI, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            records.append(json.loads(line))

company_map = {}
with engine.connect() as conn:
    rows = conn.execute(text('''
        SELECT company_id, LOWER(TRIM(legal_name))
        FROM companies
        WHERE is_ankara = TRUE AND data_quality_score BETWEEN 40 AND 59
    ''')).fetchall()
    for cid, name in rows:
        company_map[name] = cid

print(f"40-59 puan araliginda firma: {len(company_map)}")

updates = []
for rec in records:
    unvan = (rec.get('unvan') or '').strip().lower()
    if not unvan:
        continue
    cid = company_map.get(unvan)
    if not cid:
        continue
    web = rec.get('web_sitesi')
    if web and web not in GENERIC:
        updates.append((cid, 'web_sitesi', web))
        updates.append((cid, 'website_domain', web))
    emails = rec.get('emailler') or []
    if emails:
        updates.append((cid, 'primary_email', emails[0]))
    phones = rec.get('telefonler') or []
    if phones:
        updates.append((cid, 'primary_phone', phones[0]))
    adres = rec.get('adres')
    if adres:
        updates.append((cid, 'adres', adres))

print(f"Hazirlanan guncelleme: {len(updates)}")
if not updates:
    raise SystemExit

from collections import defaultdict
by_col = defaultdict(list)
for cid, col, val in updates:
    by_col[col].append((cid, val))

conn = psycopg2.connect(db_url)
conn.autocommit = False
cur = conn.cursor()

for col, pairs in by_col.items():
    sql = f'UPDATE companies SET {col} = data.val FROM (VALUES %s) AS data(cid, val) WHERE company_id = data.cid'
    execute_values(cur, sql, pairs, template=None, page_size=1000)
    print(f"{col}: {len(pairs)} guncelleme")

conn.commit()
conn.close()
print("P3-3 batch guncelleme tamamlandi")
