import json, re, os
from pathlib import Path
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
load_dotenv(root / '.env')
db_url = os.getenv('DATABASE_URL')

from sqlalchemy import create_engine
from sqlalchemy.sql import text

engine = create_engine(db_url, echo=False, future=True)

DETAYLI = root / 'data/ostim/firmalar_detayli.jsonl'
VKN_PATTERN = re.compile(r'\b(\d{10,11})\b')

records = []
with open(DETAYLI, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            records.append(json.loads(line))

vkn_count = 0
with engine.connect() as conn:
    for rec in records:
        unvan = (rec.get('unvan') or '').strip()
        if not unvan:
            continue
        vkn = None
        for field in ['web_sitesi', 'telefonler', 'emailler', 'adres', 'yetkili', 'sosyal_medya']:
            val = rec.get(field)
            if val is None:
                continue
            text_val = ' '.join(val) if isinstance(val, list) else str(val)
            m = VKN_PATTERN.search(text_val)
            if m and len(m.group(1)) in (10, 11):
                vkn = m.group(1)
                break
        if not vkn:
            continue
        row = conn.execute(
            text("SELECT company_id FROM companies WHERE LOWER(TRIM(legal_name)) = LOWER(:n) LIMIT 1"),
            {"n": unvan}
        ).first()
        if not row:
            continue
        conn.execute(
            text("UPDATE companies SET tax_number = COALESCE(:vkn, tax_number), vergi_no = COALESCE(:vkn, vergi_no) WHERE company_id = :cid"),
            {"vkn": vkn, "cid": row[0]}
        )
        vkn_count += 1
    conn.commit()
print(f'Yazilan VKN: {vkn_count}')
