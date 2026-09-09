import json, os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT = Path('.').resolve()
load_dotenv(ROOT / '.env')
engine = create_engine(os.getenv('DATABASE_URL'), future=True)

vkn_data = []
with open('data/merged/vkn_web_bulunan_v2.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        rec = json.loads(line)
        vkn = rec.get('vkn', [''])[0] if rec.get('vkn') else ''
        cid = rec.get('company_id')
        if vkn and cid:
            vkn_data.append({'cid': cid, 'vkn': vkn})

print(f'Yuklenecek VKN: {len(vkn_data)}')

with engine.begin() as conn:
    for u in vkn_data:
        conn.execute(text('''
            UPDATE companies SET vergi_no = :vkn, tax_number = :vkn
            WHERE company_id = :cid AND (vergi_no IS NULL OR vergi_no = '')
        '''), u)
        conn.execute(text('''
            UPDATE source_records sr SET raw_tax_number = COALESCE(raw_tax_number, :vkn)
            FROM companies c WHERE sr.source_record_id = c.source_record_id AND c.company_id = :cid
        '''), u)
    print('VKN yuklendi')

engine.dispose()
