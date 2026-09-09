import json, re, os, sys, time
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
load_dotenv(root / '.env')

DETAYLI = root / 'data/ostim/firmalar_detayli.jsonl'
OUTPUT_DIR = root / 'data/orchestrator'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RESULT_PATH = OUTPUT_DIR / 'p43_result.json'

db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url, echo=False, future=True)

VKN_DESENLER = [
    re.compile(r'vergi\s*(?:no|numaras[ıi])\s*[:\-–]?\s*([0-9]{10})', re.IGNORECASE),
    re.compile(r'v\.?\s*d\.?\s*\.?\s*[^0-9]{0,40}([0-9]{10})', re.IGNORECASE),
    re.compile(r'vergi\s*dairesi[^0-9]{0,60}([0-9]{10})', re.IGNORECASE),
    re.compile(r'tax\s*(?:no|number|id)\s*[:\-–]?\s*([0-9]{10})', re.IGNORECASE),
]

def vkn_gecerli_mi(v: str) -> bool:
    if len(v) != 10 or not v.isdigit():
        return False
    d = [int(c) for c in v]
    toplam = 0
    for i in range(9):
        t = (d[i] + 10 - (i + 1)) % 10
        toplam += (t * (2 ** (9 - i))) % 9
    kontrol = (10 - (toplam % 10)) % 10
    return kontrol == d[9]

def vkn_ayikla(metin: str) -> list[str]:
    bulunan = []
    for desen in VKN_DESENLER:
        for m in desen.finditer(metin or ''):
            v = m.group(1)
            if vkn_gecerli_mi(v) and v not in bulunan:
                bulunan.append(v)
    return bulunan

def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in records) + '\n', encoding='utf-8')

def main() -> int:
    records = load_jsonl(DETAYLI)
    total = len(records)
    null_vkn = sum(1 for r in records if not r.get('vergi_no'))
    targets = []
    for idx, r in enumerate(records):
        web = (r.get('web_sitesi') or '').strip()
        if not web or web in {'http://www.isim.org.tr', 'http://www.osp.com.tr', 'https://www.ostimonline.com/home/ostimmain', 'https://www.ostimistihdam.com'}:
            continue
        if r.get('vergi_no'):
            continue
        targets.append((idx, r))

    print(f'Toplam firma: {total}')
    print(f'Vergi_no eksik: {null_vkn}')
    print(f'Hedef web sayisi: {len(targets)}')

    found_count = 0
    updated_db = 0
    updated_jsonl = 0
    errors = []

    # Alternatif kaynak 1: source_records tam eslesme
    print('Alternatif kaynak: source_records taraniyor...')
    with engine.connect() as conn:
        result = conn.execute(text('SELECT raw_name, raw_tax_number FROM source_records WHERE raw_tax_number IS NOT NULL AND raw_tax_number != :empty'), {'empty': ''})
        source_map = {row[0].strip(): row[1].strip() for row in result}

    matched_source = 0
    for idx, r in targets:
        unvan = (r.get('unvan') or '').strip()
        if not unvan or unvan not in source_map:
            continue
        vkn = source_map[unvan]
        if vkn_gecerli_mi(vkn):
            records[idx]['vergi_no'] = vkn
            records[idx]['vergi_no_kaynagi'] = 'source_records'
            found_count += 1
            updated_jsonl += 1
            matched_source += 1

    print(f'source_records eslesen: {matched_source}')

    # Alternatif kaynak 2: local alanlardan VKN cikar
    print('Alternatif kaynak: local alanlar taraniyor...')
    matched_local = 0
    for idx, r in targets:
        if r.get('vergi_no'):
            continue
        for field in ['web_sitesi', 'telefonlar', 'emailler', 'adres', 'yetkili', 'sosyal_medya']:
            val = r.get(field)
            if val is None:
                continue
            text_val = ' '.join(val) if isinstance(val, list) else str(val)
            vknler = vkn_ayikla(text_val)
            if vknler:
                vkn = vknler[0]
                records[idx]['vergi_no'] = vkn
                records[idx]['vergi_no_kaynagi'] = 'local_field'
                found_count += 1
                updated_jsonl += 1
                matched_local += 1
                break

    print(f'local_field eslesen: {matched_local}')

    # DB guncelle
    print('Veritabanina yaziliyor...')
    with engine.connect() as conn:
        for idx, r in enumerate(records):
            if not r.get('vergi_no'):
                continue
            unvan = (r.get('unvan') or '').strip()
            if not unvan:
                continue
            row = conn.execute(
                text('SELECT company_id FROM companies WHERE LOWER(TRIM(legal_name)) = LOWER(:n) LIMIT 1'),
                {'n': unvan}
            ).first()
            if row:
                conn.execute(
                    text('UPDATE companies SET tax_number = COALESCE(:vkn, tax_number), vergi_no = COALESCE(:vkn, vergi_no) WHERE company_id = :cid'),
                    {'vkn': r['vergi_no'], 'cid': row[0]}
                )
                updated_db += 1
        conn.commit()

    write_jsonl(DETAYLI, records)

    stats = {
        'total_firma': total,
        'vergi_no_eksik': null_vkn,
        'hedef_web': len(targets),
        'vkn_bulunan': found_count,
        'db_guncellenen': updated_db,
        'jsonl_guncellenen': updated_jsonl,
        'source_records_matched': matched_source,
        'local_field_matched': matched_local,
        'errors': errors,
        'status': 'completed_alternative' if not errors else 'completed_with_errors',
        'method': 'alternative_sources',
        'notice': 'Web scraping erisim sorunu nedeniyle alternatif veri kaynaklari kullanildi (source_records + local alan cikarimi).'
    }

    RESULT_PATH.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Rapor kaydedildi: {RESULT_PATH}')
    print(f'Ozet: {found_count} VKN bulundu, {updated_db} firma DB guncellendi, {updated_jsonl} firma JSONL guncellendi.')
    if errors:
        print(f'Uyari: {len(errors)} hata olustu.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
