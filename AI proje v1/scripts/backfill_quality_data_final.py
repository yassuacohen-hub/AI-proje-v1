# -*- coding: utf-8 -*-
import os, json, re, time
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data/orchestrator"
OUT_DIR.mkdir(parents=True, exist_ok=True)

VKN_PATTERN = re.compile(r'^\d{10,11}$')

def load_jsonl(path):
    records = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass
    return records

def normalize_name(name):
    if not name:
        return ''
    n = name.strip().lower()
    n = re.sub(r'\s+', ' ', n)
    return n

jsonl_sources = [
    'data/ostim/firmalar_detayli.jsonl',
    'data/ostim/firmalar_vkn_ekli.jsonl',
    'data/ostim/firmalar_sayfa1.jsonl',
    'data/ostim/firmalar_detailed.jsonl',
    'data/aso/aso_full.jsonl',
    'data/ostim/firmalar_full.jsonl',
    'data/baskent/firmalar.jsonl',
    'data/merged/multi_osb_merged.jsonl',
]

name_lookup = {}
load_start = time.time()
for fpath in jsonl_sources:
    p = ROOT / fpath
    if not p.exists():
        print(f'  [UYARI] Bulunamadi: {fpath}')
        continue
    recs = load_jsonl(p)
    print(f'  Yuklendi: {fpath} -> {len(recs)} kayit')
    for r in recs:
        unvan = normalize_name(r.get('unvan') or r.get('name') or r.get('firma'))
        if not unvan:
            continue
        priority = 0
        if r.get('vergi_no') and VKN_PATTERN.match(str(r['vergi_no']).strip()):
            priority += 100
        if r.get('adres') and str(r['adres']).strip():
            priority += 5
        if r.get('web_sitesi') and str(r['web_sitesi']).strip():
            priority += 3
        if r.get('telefonler') or r.get('telefonlar'):
            priority += 2
        if r.get('emailler') or r.get('eposta'):
            priority += 2
        if r.get('sektor') and str(r['sektor']).strip():
            priority += 1
        if unvan not in name_lookup or name_lookup[unvan][1] < priority:
            name_lookup[unvan] = (r, priority)

print(f'Isim esleme tablosu: {len(name_lookup)} kayit ({time.time()-load_start:.1f}s)')

load_dotenv(ROOT / '.env')
engine = create_engine(os.getenv('DATABASE_URL'), future=True)

stats = {}
with engine.connect() as conn:
    stats['total_ankara'] = conn.execute(text('SELECT COUNT(*) FROM companies WHERE is_ankara=TRUE')).scalar()
    stats['zero_score_before'] = conn.execute(text('SELECT COUNT(*) FROM companies WHERE is_ankara=TRUE AND data_quality_score=0')).scalar()
    stats['avg_before'] = float(conn.execute(text('SELECT AVG(data_quality_score) FROM companies WHERE is_ankara=TRUE')).scalar())
    print(f'Once: toplam={stats["total_ankara"]}, sifir_puan={stats["zero_score_before"]}, ortalama={stats["avg_before"]:.2f}')

# === Step 1: Phone + Email + Nace from raw_payload ===
print('\n=== Adim 1: Phone + Email + Nace backfill ===')
with engine.begin() as conn:
    r = conn.execute(text('''
        UPDATE companies c
        SET primary_phone = COALESCE(c.primary_phone, sr.raw_payload->>'telefonler')
        FROM source_records sr
        WHERE c.source_record_id = sr.source_record_id AND c.is_ankara = TRUE
        AND (c.primary_phone IS NULL OR c.primary_phone = '')
        AND sr.raw_payload->>'telefonler' IS NOT NULL AND sr.raw_payload->>'telefonler' != ''
    '''))
    stats['phone_from_raw'] = r.rowcount
    print(f'  raw_payload telefon: {r.rowcount}')

    r = conn.execute(text('''
        UPDATE companies c
        SET primary_email = COALESCE(c.primary_email, sr.raw_payload->>'emailler')
        FROM source_records sr
        WHERE c.source_record_id = sr.source_record_id AND c.is_ankara = TRUE
        AND (c.primary_email IS NULL OR c.primary_email = '')
        AND sr.raw_payload->>'emailler' IS NOT NULL AND sr.raw_payload->>'emailler' != ''
    '''))
    stats['email_from_raw'] = r.rowcount
    print(f'  raw_payload eposta: {r.rowcount}')

    conn.execute(text('''
        UPDATE source_records sr
        SET raw_phone = COALESCE(sr.raw_phone, sr.raw_payload->>'telefonler'),
            raw_email = COALESCE(sr.raw_email, sr.raw_payload->>'emailler')
        FROM companies c WHERE c.source_record_id = sr.source_record_id AND c.is_ankara = TRUE
    '''))

    conn.execute(text('''
        UPDATE source_records sr
        SET raw_nace = COALESCE(sr.raw_nace, sr.raw_payload->>'nace_code')
        FROM companies c WHERE c.source_record_id = sr.source_record_id AND c.is_ankara = TRUE
    '''))

# === Step 2: JSONL name matching ===
print('\n=== Adim 2: JSONL isim esleme ===')

with engine.connect() as conn:
    companies = conn.execute(text('''
        SELECT c.company_id, LOWER(TRIM(c.legal_name)) as ln, LOWER(TRIM(c.trade_name)) as tn
        FROM companies c WHERE c.is_ankara = TRUE
    ''')).fetchall()
    print(f'  Eslenecek firma sayisi: {len(companies)}')

    adres_data = []
    web_data = []
    sektor_data = []
    vkn_data = []
    phone_data = []
    email_data = []
    nace_data = []

    for row in companies:
        cid = str(row[0])
        ln = (row[1] or '').strip()
        tn = (row[2] or '').strip()
        matched = name_lookup.get(ln) or name_lookup.get(tn)
        if not matched:
            continue
        rec = matched[0]

        vkn = str(rec.get('vergi_no') or '').strip()
        if vkn and VKN_PATTERN.match(vkn):
            vkn_data.append({'cid': cid, 'val': vkn})

        adres = str(rec.get('adres') or '').strip()
        if adres:
            adres_data.append({'cid': cid, 'val': adres})

        web = str(rec.get('web_sitesi') or '').strip()
        if web:
            web_data.append({'cid': cid, 'val': web})

        sektor = str(rec.get('sektor') or '').strip()
        if sektor:
            sektor_data.append({'cid': cid, 'val': sektor})

        phone = str(rec.get('telefonler') or rec.get('telefonlar') or '').strip()
        if phone and phone not in ('[]', 'None'):
            phone_data.append({'cid': cid, 'val': phone})

        email = str(rec.get('emailler') or rec.get('eposta') or '').strip()
        if email and email not in ('[]', 'None'):
            email_data.append({'cid': cid, 'val': email})

        nace = str(rec.get('naceKod') or rec.get('nace_code') or rec.get('nace_kod') or '').strip()
        if nace:
            nace_data.append({'cid': cid, 'val': nace})

    print(f'  Eslesme: vkn={len(vkn_data)}, adres={len(adres_data)}, web={len(web_data)}, sektor={len(sektor_data)}, phone={len(phone_data)}, email={len(email_data)}, nace={len(nace_data)}')

    def bulk_update(field_type, data_list, update_sql):
        if not data_list:
            return 0
        print(f'  {field_type}: {len(data_list)} kayit guncellenecek...', end=' ', flush=True)
        t0 = time.time()
        with engine.begin() as conn2:
            conn2.execute(text('DROP TABLE IF EXISTS _backfill_temp'))
            conn2.execute(text('''
                CREATE TEMP TABLE _backfill_temp (
                    cid UUID, field_type TEXT, val TEXT
                )
            '''))
            batch_size = 2000
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i+batch_size]
                values = []
                params = {}
                for j, d in enumerate(batch):
                    k = f'c{i+j}'
                    f = f'f{i+j}'
                    v = f'v{i+j}'
                    values.append(f'(:{k}, :{f}, :{v})')
                    params[k] = d['cid']
                    params[f] = field_type
                    params[v] = d['val']
                sql = 'INSERT INTO _backfill_temp (cid, field_type, val) VALUES ' + ', '.join(values)
                conn2.execute(text(sql), params)
            conn2.execute(text(update_sql))
            conn2.execute(text('DROP TABLE IF EXISTS _backfill_temp'))
        elapsed = time.time() - t0
        print(f'{elapsed:.1f}s')
        return len(data_list)

    stats['adres_from_jsonl'] = bulk_update('adres', adres_data, '''
        UPDATE companies c SET adres = COALESCE(c.adres, t.val)
        FROM (SELECT cid, val FROM _backfill_temp WHERE field_type = 'adres') t
        WHERE c.company_id = t.cid AND (c.adres IS NULL OR c.adres = '')
    ''')

    stats['web_from_jsonl'] = bulk_update('web', web_data, '''
        UPDATE companies c SET website_domain = COALESCE(c.website_domain, t.val),
                               web_sitesi = COALESCE(c.web_sitesi, t.val)
        FROM (SELECT cid, val FROM _backfill_temp WHERE field_type = 'web') t
        WHERE c.company_id = t.cid
        AND (c.website_domain IS NULL OR c.website_domain = '')
        AND (c.web_sitesi IS NULL OR c.web_sitesi = '')
    ''')

    stats['vkn_from_jsonl'] = bulk_update('vkn', vkn_data, '''
        UPDATE companies c SET vergi_no = COALESCE(c.vergi_no, t.val),
                               tax_number = COALESCE(c.tax_number, t.val)
        FROM (SELECT cid, val FROM _backfill_temp WHERE field_type = 'vkn') t
        WHERE c.company_id = t.cid
        AND (c.vergi_no IS NULL OR c.vergi_no = '')
    ''')

    stats['phone_from_jsonl'] = bulk_update('phone', phone_data, '''
        UPDATE companies c SET primary_phone = COALESCE(c.primary_phone, t.val)
        FROM (SELECT cid, val FROM _backfill_temp WHERE field_type = 'phone') t
        WHERE c.company_id = t.cid AND (c.primary_phone IS NULL OR c.primary_phone = '')
    ''')

    stats['email_from_jsonl'] = bulk_update('email', email_data, '''
        UPDATE companies c SET primary_email = COALESCE(c.primary_email, t.val)
        FROM (SELECT cid, val FROM _backfill_temp WHERE field_type = 'email') t
        WHERE c.company_id = t.cid AND (c.primary_email IS NULL OR c.primary_email = '')
    ''')

    stats['sektor_from_jsonl'] = bulk_update('sektor', sektor_data, '''
        UPDATE source_records sr
        SET raw_payload = raw_payload || jsonb_build_object('sektor', t.val)
        FROM companies c, (SELECT cid, val FROM _backfill_temp WHERE field_type = 'sektor') t
        WHERE sr.source_record_id = c.source_record_id AND c.company_id = t.cid
        AND (sr.raw_payload->>'sektor' IS NULL OR sr.raw_payload->>'sektor' = '')
    ''')

    stats['nace_from_jsonl'] = bulk_update('nace', nace_data, '''
        UPDATE source_records sr
        SET raw_nace = COALESCE(sr.raw_nace, t.val)
        FROM companies c, (SELECT cid, val FROM _backfill_temp WHERE field_type = 'nace') t
        WHERE sr.source_record_id = c.source_record_id AND c.company_id = t.cid
        AND (sr.raw_nace IS NULL OR sr.raw_nace = '')
    ''')

# === Step 3: VKN from address matching ===
print('\n=== Adim 3: VKN adres esleme ===')
sayfa1 = load_jsonl('data/ostim/firmalar_sayfa1.jsonl')
addr_to_vkn = {}
for r in sayfa1:
    vkn = str(r.get('vergi_no') or '').strip()
    addr = str(r.get('adres') or '').strip()
    if vkn and VKN_PATTERN.match(vkn) and addr:
        addr_norm = re.sub(r'\s+', ' ', addr.strip().lower()).replace('.', '').replace(',', '')
        if len(addr_norm) > 5:
            addr_to_vkn[addr_norm] = vkn
print(f'  VKN-adres ciftleri: {len(addr_to_vkn)}')

def normalize_addr(s):
    if not s:
        return ''
    s = s.strip().lower()
    s = re.sub(r'\s+', ' ', s)
    s = s.replace('.', '').replace(',', '')
    return s

with engine.connect() as conn:
    rows_no_vkn = conn.execute(text('''
        SELECT c.company_id, LOWER(TRIM(c.adres)) as adres
        FROM companies c WHERE c.is_ankara=TRUE
        AND (c.vergi_no IS NULL OR c.vergi_no = '')
        AND (c.tax_number IS NULL OR c.tax_number = '')
    ''')).fetchall()
    print(f'  VKN olmayan firma sayisi: {len(rows_no_vkn)}')

vkn_addr_updates = []
for row in rows_no_vkn:
    cid = str(row[0])
    addr = normalize_addr(row[1] or '')
    if not addr:
        continue
    for jsonl_addr, vkn in addr_to_vkn.items():
        if addr in jsonl_addr or jsonl_addr in addr:
            if len(addr) >= 8 and len(jsonl_addr) >= 8:
                overlap = len(set(addr.split()) & set(jsonl_addr.split()))
                if overlap >= 2:
                    vkn_addr_updates.append({'cid': cid, 'vkn': vkn})
                    break

print(f'  Adres ile eslesen VKN: {len(vkn_addr_updates)}')

if vkn_addr_updates:
    with engine.begin() as conn:
        for u in vkn_addr_updates:
            conn.execute(text('''
                UPDATE companies SET vergi_no = :vkn, tax_number = :vkn
                WHERE company_id = :cid AND (vergi_no IS NULL OR vergi_no = '')
            '''), u)
            conn.execute(text('''
                UPDATE source_records sr SET raw_tax_number = COALESCE(raw_tax_number, :vkn)
                FROM companies c WHERE sr.source_record_id = c.source_record_id AND c.company_id = :cid
            '''), u)

stats['vkn_by_address'] = len(vkn_addr_updates)
stats['vkn_backfilled'] = len(vkn_data) + len(vkn_addr_updates)

# === Summary ===
with engine.connect() as conn:
    stats['avg_after_without_recalc'] = float(conn.execute(text('SELECT AVG(data_quality_score) FROM companies WHERE is_ankara=TRUE')).scalar())

stats_path = OUT_DIR / 'backfill_stats.json'
with open(stats_path, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2, ensure_ascii=False, default=str)

print('\n=== Ozet ===')
print(json.dumps(stats, indent=2, ensure_ascii=False, default=str))
print(f'\nIstatistikler kaydedildi: {stats_path}')
