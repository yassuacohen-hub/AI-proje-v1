import json, time, requests
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DETAYLI = ROOT / 'data' / 'ostim' / 'firmalar_detayli.jsonl'
GENERIC = {
    'http://www.isim.org.tr', 'http://www.osp.com.tr',
    'https://www.ostimonline.com/home/ostimmain',
}
HEADERS = {'User-Agent': 'AnkaraB2B-Bot/1.0'}
TIMEOUT = 15


def extract_detail(slug: str) -> dict:
    url = f'https://www.ostim.org.tr/firmalar/{slug}'
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 404:
            return {}
        r.raise_for_status()
    except Exception:
        return {}
    soup = BeautifulSoup(r.text, 'html.parser')
    data = {'web_sitesi': None, 'adres': None, 'vergi_no': None, 'osb_parsel': None}
    for a in soup.select('a[href^="http"]'):
        href = a.get('href', '')
        low = href.lower()
        if any(b in low for b in ['ostim.org.tr', 'ostimonline.com', 'ostimradyo.com', 'isim.org.tr', 'osp.com.tr', 'facebook.com', 'twitter.com', 'x.com', 'linkedin.com', 'instagram.com', 'youtube.com']):
            continue
        if low.endswith(('/', '/index.html', '/home')):
            continue
        data['web_sitesi'] = href
        break
    for label in ['Adres', 'Adresi', 'Vergi No', 'Vergi', 'Ada / Parsel', 'Ada', 'Parsel']:
        el = soup.find(string=__import__('re').compile(label, __import__('re').IGNORECASE))
        if el and el.parent:
            ns = el.parent.find_next_sibling()
            val = ns.get_text(strip=True) if ns else el.parent.get_text(strip=True).replace(label, '').strip(' :')
            if not val:
                continue
            key = 'adres' if 'adres' in label.lower() else ('vergi_no' if 'vergi' in label.lower() else 'osb_parsel')
            data[key] = val
    return data


def main():
    if not DETAYLI.exists():
        print('Dosya yok:', DETAYLI)
        return
    records = []
    with open(DETAYLI, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    print(f'Toplam kayit: {len(records)}')
    targets = [i for i, r in enumerate(records) if r.get('web_sitesi') in GENERIC]
    print(f'Yeniden kazinicak: {len(targets)}')
    done = 0
    for idx in targets:
        rec = records[idx]
        slug = rec.get('slug')
        if not slug:
            continue
        det = extract_detail(slug)
        if det.get('web_sitesi'):
            rec['web_sitesi'] = det['web_sitesi']
        if det.get('adres') and not rec.get('adres'):
            rec['adres'] = det['adres']
        if det.get('vergi_no') and not rec.get('vergi_no'):
            rec['vergi_no'] = det['vergi_no']
        if det.get('osb_parsel') and not rec.get('osb_parsel'):
            rec['osb_parsel'] = det['osb_parsel']
        done += 1
        if done % 25 == 0:
            print(f'{done}/{len(targets)}')
            with open(DETAYLI, 'w', encoding='utf-8') as f:
                for r in records:
                    f.write(json.dumps(r, ensure_ascii=False) + '\n')
        time.sleep(0.5)
    with open(DETAYLI, 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f'Tamam! {done} kayit guncellendi.')


if __name__ == '__main__':
    main()
