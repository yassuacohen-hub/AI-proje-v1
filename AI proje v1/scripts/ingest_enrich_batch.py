import json, os
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

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
    rows = conn.execute(text('SELECT company_id, LOWER(TRIM(legal_name)), source_record_id FROM companies WHERE is_ankara = TRUE')).fetchall()
    for cid, name, sid in rows:
        company_map[name] = (cid, sid)

rows = []
for rec in records:
    unvan = (rec.get('unvan') or '').strip().lower()
    if not unvan:
        continue
    info = company_map.get(unvan)
    if not info:
        continue
    cid, sid = info
    web = rec.get('web_sitesi')
    if web and web not in GENERIC:
        rows.append((cid, 'web_sitesi', web))
        rows.append((cid, 'website_domain', web))
    emails = rec.get('emailler') or []
    if emails:
        rows.append((cid, 'primary_email', emails[0]))
    phones = rec.get('telefonler') or []
    if phones:
        rows.append((cid, 'primary_phone', phones[0]))
    adres = rec.get('adres')
    if adres:
        rows.append((cid, 'adres', adres))

print(f'Toplam guncelleme satiri: {len(rows)}')
if not rows:
    raise SystemExit

from collections import defaultdict
by_col = defaultdict(list)
for cid, col, val in rows:
    by_col[col].append((cid, val))

total = 0
with engine.connect() as conn:
    for col, pairs in by_col.items():
        if col == 'adres':
            continue
        values_sql = ','.join([f"({cid}, '{val.replace(chr(39), chr(39)+chr(39))}')" for cid, val in pairs])
        sql = f'''
            UPDATE companies c
            SET {col} = v.val
            FROM (VALUES {values_sql}) AS v(cid, val)
            WHERE c.company_id = v.cid
        '''
        result = conn.execute(text(sql))
        total += result.rowcount
    conn.commit()
print(f'Guncellenen toplam: {total}')
