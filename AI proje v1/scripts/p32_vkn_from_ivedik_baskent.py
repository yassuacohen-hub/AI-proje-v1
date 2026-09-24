import json, re, time, os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from rapidfuzz import fuzz
from sqlalchemy import create_engine, text
import warnings
warnings.filterwarnings('ignore')
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
load_dotenv(root / '.env')
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url, echo=False, future=True)

IVEDIK = root / 'data/ivedik/firmalar.jsonl'
BASKENT = root / 'data/baskent/firmalar.jsonl'
OUTPUT_DIR = root / 'data/orchestrator'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
VKN_PATTERN = re.compile(r"\b(\d{10,11})\b")
HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 5
MAX_WORKERS = 6
FUZZY_THRESHOLD = 0.80

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


def normalize_name(name: str) -> str:
    name = name.translate(TURKISH_CHAR_MAP)
    name = name.lower()
    name = re.sub(r'[^\w\s]', '', name)
    tokens = [t for t in name.split() if t and t not in ABBREVIATIONS]
    return ' '.join(tokens)


def fuzzy_match(query: str, candidates: list[str], threshold: float = FUZZY_THRESHOLD) -> str | None:
    q = normalize_name(query)
    best = None
    best_score = 0.0
    for c in candidates:
        score = fuzz.ratio(q, c) / 100.0
        if score > best_score:
            best_score = score
            best = c
    if best_score >= threshold:
        return best
    return None


def extract_vkn_from_text(text: str) -> str | None:
    for m in VKN_PATTERN.finditer(text):
        v = m.group(1)
        s = max(0, m.start() - 120)
        e = min(len(text), m.end() + 120)
        ctx = text[s:e].lower()
        if any(k in ctx for k in ["vergi no", "vergi dairesi", "tax number", "tax id", "vkn", "vergi numarasi"]):
            if len(v) in (10, 11):
                return v
    return None


def fetch_vkn_from_url(url: str) -> str | None:
    try:
        import requests
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            return extract_vkn_from_text(r.text)
    except Exception:
        pass
    return None


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    ivedik_records = load_jsonl(IVEDIK)
    baskent_records = load_jsonl(BASKENT)

    company_map = {}
    normalized_index: dict[str, list[tuple[str, str]]] = {}
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT company_id, legal_name, source_record_id FROM companies WHERE is_ankara = TRUE")).fetchall()
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
        'errors': [],
    }

    for source, records in [("ivedik", ivedik_records), ("baskent", baskent_records)]:
        print(f"=== {source}: {len(records)} firma ===")
        targets = []
        for rec in records:
            unvan = (rec.get("unvan") or "").strip()
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
                    candidate = fuzzy_match(unvan, list(normalized_index.keys()))
                    if candidate:
                        info = normalized_index[candidate][0]
                        match_type = 'fuzzy'

            if not info:
                continue
            cid, sid = info

            if rec.get("vergi_no"):
                stats[f'{source}_skipped_has_vkn'] += 1
                continue

            url = rec.get("web_sitesi") or (f"https://www.ivedikosb.org.tr/firmalar/{rec['slug']}" if source == "ivedik" and rec.get("slug") else None)
            if not url:
                stats[f'{source}_skipped_no_url'] += 1
                continue

            if match_type == 'exact':
                stats[f'{source}_exact'] += 1
            elif match_type == 'fuzzy':
                stats[f'{source}_fuzzy'] += 1
            targets.append((cid, sid, url))

        print(f"  Hedef: {len(targets)} (exact: {stats[f'{source}_exact']}, fuzzy: {stats[f'{source}_fuzzy']})")
        found = 0
        for i in range(0, len(targets), 20):
            chunk = targets[i:i + 20]
            results = {}
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_map = {executor.submit(fetch_vkn_from_url, url): (cid, sid) for cid, sid, url in chunk}
                for future in as_completed(future_map):
                    cid, sid = future_map[future]
                    try:
                        results[(cid, sid)] = future.result()
                    except Exception as e:
                        results[(cid, sid)] = None
                        stats['errors'].append(f"{source} | {cid} | {e}")

            with engine.connect() as conn:
                for (cid, sid), vkn in results.items():
                    if not vkn:
                        continue
                    conn.execute(
                        text("UPDATE companies SET tax_number = COALESCE(:vkn, tax_number), vergi_no = COALESCE(:vkn, vergi_no) WHERE company_id = :cid"),
                        {"vkn": vkn, "cid": cid},
                    )
                    found += 1
                conn.commit()
            total_found = stats[f'{source}_vkn_found'] + found
            stats[f'{source}_vkn_found'] = total_found
            print(f"  {min(i + 20, len(targets))}/{len(targets)} | bulunan: {total_found}")
            time.sleep(1)
        print(f"  {source} toplam yeni VKN: {total_found}")

    stats['total_vkn_found'] = stats['ivedik_vkn_found'] + stats['baskent_vkn_found']
    stats['matched_companies'] = (stats['ivedik_exact'] + stats['baskent_exact'] +
                                   stats['ivedik_fuzzy'] + stats['baskent_fuzzy'])
    stats['vkn_found'] = stats['total_vkn_found']

    note_parts = []
    if stats['ivedik_vkn_found'] == 0 and stats['ivedik_skipped_no_url'] < stats['ivedik_exact'] + stats['ivedik_fuzzy']:
        note_parts.append('ivedikosb.org.tr detay sayfalarina erisim saglanamadi (baglanti kesildi)')
    if stats['total_vkn_found'] == 0:
        note_parts.append('Baskent firmalari tarandi ancak VKN bulunamadi')
    stats['note'] = '. '.join(note_parts) if note_parts else 'Basariyla islendi.'

    summary_path = OUTPUT_DIR / 'p32_vkn_matching_report.json'
    p32_path = OUTPUT_DIR / 'p32_result.json'
    p32_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
    summary_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Rapor kaydedildi: {summary_path}")
    print(f"Genel toplam yeni VKN: {stats['total_vkn_found']}")
    if stats['errors']:
        print(f"Uyarı: {len(stats['errors'])} hata oluştu, detaylar raporda.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

