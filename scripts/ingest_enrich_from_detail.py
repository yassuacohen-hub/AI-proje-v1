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

updated = 0
with engine.connect() as conn:
    for rec in records:
        unvan = (rec.get('unvan') or '').strip()
        if not unvan:
            continue
        row = conn.execute(
            text('SELECT company_id FROM companies WHERE LOWER(TRIM(legal_name)) = LOWER(:n) LIMIT 1'),
            {'n': unvan}
        ).first()
        if not row:
            continue
        cid = row[0]
        web = rec.get('web_sitesi')
        if web and web not in GENERIC:
            conn.execute(text('UPDATE companies SET web_sitesi = COALESCE(:web, web_sitesi), website_domain = COALESCE(:web, website_domain) WHERE company_id = :cid'), {'web': web, 'cid': cid})
        emails = rec.get('emailler') or []
        if emails:
            conn.execute(text('UPDATE companies SET primary_email = COALESCE(:email, primary_email) WHERE company_id = :cid'), {'email': emails[0], 'cid': cid})
        phones = rec.get('telefonler') or []
        if phones:
            conn.execute(text('UPDATE companies SET primary_phone = COALESCE(:phone, primary_phone) WHERE company_id = :cid'), {'phone': phones[0], 'cid': cid})
        adres = rec.get('adres')
        if adres:
            pass
        updated += 1
    conn.commit()
print(f'Guncellenen firma sayisi: {updated}')
