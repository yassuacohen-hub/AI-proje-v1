import json, re, time, os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
load_dotenv(root / '.env')
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url, echo=False, future=True)

DETAYLI = root / 'data/ostim/firmalar_detayli.jsonl'
GENERIC = {'http://www.isim.org.tr', 'http://www.osp.com.tr', 'https://www.ostimonline.com/home/ostimmain'}
VKN_PATTERN = re.compile(r'\b(\d{10,11})\b')
HEADERS = {'User-Agent': 'AnkaraB2B-Bot/1.0'}
TIMEOUT = 10
MAX_WORKERS = 8


def extract_vkn_from_html(html: str) -> str | None:
    for m in VKN_PATTERN.finditer(html):
        v = m.group(1)
        s = max(0, m.start() - 120)
        e = min(len(html), m.end() + 120)
        ctx = html[s:e].lower()
        if any(k in ctx for k in ['vergi no', 'vergi dairesi', 'tax number', 'tax id', 'vkn', 'vergi numarasi']):
            if len(v) in (10, 11):
                return v
    return None


def fetch_and_extract(web: str) -> str | None:
    try:
        import requests
        r = requests.get(web, headers=HEADERS, timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            return extract_vkn_from_html(r.text)
    except Exception:
        pass
    return None


def main():
    records = []
    with open(DETAYLI, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    targets = []
    for idx, r in enumerate(records):
        web = r.get('web_sitesi')
        if not web or web in GENERIC:
            continue
        targets.append((idx, r))

    print(f'Hedef web sayisi: {len(targets)}')
    found = 0
    batch = 50

    for i in range(0, len(targets), batch):
        chunk = targets[i:i+batch]
        results = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_map = {
                executor.submit(fetch_and_extract, web): (idx, unvan)
                for idx, r in chunk
                for web in [r.get('web_sitesi')]
                for unvan in [r.get('unvan')]
            }
            for future in as_completed(future_map):
                idx, unvan = future_map[future]
                try:
                    vkn = future.result()
                except Exception:
                    vkn = None
                results[idx] = vkn

        with engine.connect() as conn:
            for idx, vkn in results.items():
                if not vkn:
                    continue
                unvan = (records[idx].get('unvan') or '').strip()
                if not unvan:
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
                found += 1
            conn.commit()
        print(f'{min(i+batch, len(targets))}/{len(targets)} | bulunan: {found}')
        time.sleep(1)

    print(f'Toplam yeni VKN: {found}')


if __name__ == '__main__':
    main()
