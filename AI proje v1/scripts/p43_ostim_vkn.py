import ssl
import json, os, re, sys, time, urllib.request, urllib.error, urllib.robotparser
from concurrent.futures import ThreadPoolExecutor, as_completed
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

UA = 'AnkaraB2B-Bot/1.0 (+research contact: site owner)'
AYRACI_YOLLAR = [
    '', '/hakkimizda', '/iletisim', '/kurumsal', '/kvkk', '/hakkinda',
    '/tr/hakkimizda', '/tr/iletisim', '/about', '/contact',
]
VKN_DESENLER = [
    re.compile(r'vergi\s*(?:no|numaras[ıi])\s*[:\-–]?\s*([0-9]{10})', re.IGNORECASE),
    re.compile(r'v\.?\s*d\.?\s*\.?\s*[^0-9]{0,40}([0-9]{10})', re.IGNORECASE),
    re.compile(r'vergi\s*dairesi[^0-9]{0,60}([0-9]{10})', re.IGNORECASE),
    re.compile(r'tax\s*(?:no|number|id)\s*[:\-–]?\s*([0-9]{10})', re.IGNORECASE),
]
GENERIC = {'http://www.isim.org.tr', 'http://www.osp.com.tr', 'https://www.ostimonline.com/home/ostimmain', 'https://www.ostimistihdam.com'}
TIMEOUT = 15
MAX_WORKERS = 6
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


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
    bulunan: list[str] = []
    for desen in VKN_DESENLER:
        for m in desen.finditer(metin or ''):
            v = m.group(1)
            if vkn_gecerli_mi(v) and v not in bulunan:
                bulunan.append(v)
    return bulunan


def _get(url: str, zaman_asimi: int = TIMEOUT) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'tr'})
    try:
        with urllib.request.urlopen(req, timeout=zaman_asimi, context=SSL_CTX) as r:
            ham = r.read()
            try:
                return r.status, ham.decode('utf-8')
            except UnicodeDecodeError:
                return r.status, ham.decode('latin-1', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        print(f'    [AG] {url} -> {type(e).__name__}. Olası neden: VPN. Gerekirse VPN kapatabilirsiniz.')
        return 0, ''


def robots_izinli_mi(domain: str, yol: str, rp_cache: dict) -> bool:
    rp = rp_cache.get(domain, '__yok__')
    if rp == '__yok__':
        durum, metin = _get(f'https://{domain}/robots.txt')
        if durum == 200 and metin:
            rp = urllib.robotparser.RobotFileParser()
            rp.parse(metin.splitlines())
        else:
            rp = False
        rp_cache[domain] = rp
    if rp is False:
        return False
    try:
        return rp.can_fetch(UA, f'https://{domain}{yol or "/"}')
    except Exception:
        return False


def site_tara(domain: str, rp_cache: dict) -> list[str]:
    bulunan: list[str] = []
    for yol in AYRACI_YOLLAR:
        if len(bulunan) >= 2:
            break
        if not robots_izinli_mi(domain, yol, rp_cache):
            continue
        durum, metin = _get(f'https://{domain}{yol}')
        if durum != 200 or not metin:
            durum, metin = _get(f'http://{domain}{yol}')
        if durum == 200 and metin:
            for v in vkn_ayikla(metin):
                if v not in bulunan:
                    bulunan.append(v)
            time.sleep(1)
    return bulunan


def domain_cikar(web: str) -> str | None:
    m = re.match(r'^https?://([^/:?#]+)', (web or '').strip(), re.IGNORECASE)
    return m.group(1).lower() if m else None


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
        if not web or web in GENERIC:
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
    rp_cache: dict = {}
    errors: list[str] = []

    batch = 20
    for i in range(0, len(targets), batch):
        chunk = targets[i:i + batch]
        results: dict[int, list[str]] = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_map = {}
            for idx, r in chunk:
                web = r.get('web_sitesi')
                dom = domain_cikar(web)
                if dom:
                    future_map[executor.submit(site_tara, dom, rp_cache)] = idx
            for future in as_completed(future_map):
                idx = future_map[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    results[idx] = []
                    errors.append(str(e))

        with engine.connect() as conn:
            for idx, vknler in results.items():
                if not vknler:
                    continue
                vkn = vknler[0]
                unvan = (records[idx].get('unvan') or '').strip()
                if not unvan:
                    continue
                row = conn.execute(
                    text('SELECT company_id FROM companies WHERE LOWER(TRIM(legal_name)) = LOWER(:n) LIMIT 1'),
                    {'n': unvan}
                ).first()
                if row:
                    conn.execute(
                        text('UPDATE companies SET tax_number = COALESCE(:vkn, tax_number), vergi_no = COALESCE(:vkn, vergi_no) WHERE company_id = :cid'),
                        {'vkn': vkn, 'cid': row[0]}
                    )
                    updated_db += 1

                records[idx]['vergi_no'] = vkn
                records[idx]['vergi_no_kaynagi'] = 'web_scrape'
                updated_jsonl += 1
                found_count += 1
            conn.commit()

        write_jsonl(DETAYLI, records)
        print(f'{min(i + batch, len(targets))}/{len(targets)} | bulunan: {found_count} | db_guncellenen: {updated_db} | jsonl_guncellenen: {updated_jsonl}')
        time.sleep(1)

    stats = {
        'total_firma': total,
        'vergi_no_eksik': null_vkn,
        'hedef_web': len(targets),
        'vkn_bulunan': found_count,
        'db_guncellenen': updated_db,
        'jsonl_guncellenen': updated_jsonl,
        'errors': errors,
        'status': 'completed' if not errors else 'completed_with_errors'
    }

    RESULT_PATH.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Rapor kaydedildi: {RESULT_PATH}')
    print(f'Ozet: {found_count} VKN bulundu, {updated_db} firma DB guncellendi, {updated_jsonl} firma JSONL guncellendi.')
    if errors:
        print(f'Uyari: {len(errors)} hata olustu.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
