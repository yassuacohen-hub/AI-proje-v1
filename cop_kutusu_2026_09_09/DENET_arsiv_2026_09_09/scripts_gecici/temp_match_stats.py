import json, re
from pathlib import Path
from rapidfuzz import fuzz
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

root = Path(__file__).resolve().parents[1]
load_dotenv(root / '.env')
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url, echo=False, future=True)

IVEDIK = root / 'data/ivedik/firmalar.jsonl'
BASKENT = root / 'data/baskent/firmalar.jsonl'

TURKISH_CHAR_MAP = str.maketrans({
    'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G', 'ü': 'u', 'Ü': 'U',
    'ş': 's', 'Ş': 'S', 'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C',
})
ABBREVIATIONS = {
    'san.', 'tic.', 'ltd.', 'şti.', 'a.ş.', 'a.s.', 'anonim', 'şirketi',
    'limited', 'şirket', 've', 'ticaret', 'sanayi', 'imalat', 'değerleme',
    'organize', 'av.', 'tur.', 'org.', 'dan.', 'kim.', 'i̇nş.', 'inş.',
    'dış', 'dis', 'iç', 'ic', 'tekstil', 'tek.', 'imal', 'ithalat', 'ihracat',
    'mühendislik', 'müh.', 'muh.', 'müşavir', 'musavir', 'hizmet', 'hizm.',
    'gıda', 'gida', 'metal', 'otomotiv', 'otom.', 'elektronik', 'elektr.',
    'yazılım', 'yazilim', 'teknoloji', 'tekno.', 'teknol.', 'mobilya',
    'mob.', 'tekstil', 'tekst.', 'tek.', 'plastik', 'kauçuk', 'kaucuk',
    'ürünler', 'urunler', 'ürün', 'urun', 'imalat', 'imal.', 'değerleme',
    'degerleme', 'değer.', 'deger.',
}

def normalize_name(name):
    name = name.translate(TURKISH_CHAR_MAP)
    name = name.lower()
    name = re.sub(r'[^\w\s]', '', name)
    tokens = [t for t in name.split() if t and t not in ABBREVIATIONS]
    return ' '.join(tokens)

def load_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

ivedik_records = load_jsonl(IVEDIK)
baskent_records = load_jsonl(BASKENT)

company_map = {}
normalized_index = {}
with engine.connect() as conn:
    rows = conn.execute(text('SELECT company_id, legal_name, source_record_id FROM companies WHERE is_ankara = TRUE')).fetchall()
    for cid, name, sid in rows:
        company_map[name] = (cid, sid)
        norm = normalize_name(name)
        normalized_index.setdefault(norm, []).append((cid, sid))

stats = {
    'ivedik_total': len(ivedik_records),
    'baskent_total': len(baskent_records),
    'ivedik_exact': 0,
    'baskent_exact': 0,
    'ivedik_fuzzy': 0,
    'baskent_fuzzy': 0,
    'ivedik_skipped_no_url': 0,
    'baskent_skipped_no_url': 0,
    'ivedik_skipped_has_vkn': 0,
    'baskent_skipped_has_vkn': 0,
    'ivedik_vkn_found': 0,
    'baskent_vkn_found': 0,
    'total_vkn_found': 0,
    'matched_companies': 0,
    'vkn_found': 0,
}

for source, records in [('ivedik', ivedik_records), ('baskent', baskent_records)]:
    targets = []
    for rec in records:
        unvan = (rec.get('unvan') or '').strip()
        if not unvan:
            continue
        info = company_map.get(unvan)
        match_type = None
        if info:
            match_type = 'exact'
        else:
            norm_unvan = normalize_name(unvan)
            if norm_unvan in normalized_index:
                info = normalized_index[norm_unvan][0]
                match_type = 'exact'
            else:
                candidate = None
                best_score = 0.0
                for c in list(normalized_index.keys()):
                    score = fuzz.ratio(norm_unvan, c) / 100.0
                    if score > best_score:
                        best_score = score
                        candidate = c
                if candidate and best_score >= 0.80:
                    info = normalized_index[candidate][0]
                    match_type = 'fuzzy'
        if not info:
            continue
        cid, sid = info
        if rec.get('vergi_no'):
            stats[source + '_skipped_has_vkn'] += 1
            continue
        url = rec.get('web_sitesi') or ('https://www.ivedikosb.org.tr/firmalar/' + rec['slug'] if source == 'ivedik' and rec.get('slug') else None)
        if not url:
            stats[source + '_skipped_no_url'] += 1
            continue
        if match_type == 'exact':
            stats[source + '_exact'] += 1
        elif match_type == 'fuzzy':
            stats[source + '_fuzzy'] += 1
        targets.append((cid, sid, url))
    print(source + ': ' + str(len(records)) + ' total, ' + str(stats[source + '_exact']) + ' exact, ' + str(stats[source + '_fuzzy']) + ' fuzzy, ' + str(stats[source + '_skipped_no_url']) + ' no_url')

stats['matched_companies'] = stats['ivedik_exact'] + stats['ivedik_fuzzy'] + stats['baskent_exact'] + stats['baskent_fuzzy']
print('matched_companies:', stats['matched_companies'])
