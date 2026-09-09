#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

VKN_PATTERN = re.compile(r'\b(\d{10,11})\b')
VKN_KEYWORDS = ['vergi no', 'vkn', 'vergi dairesi', 'tax number', 'tax id', 'tc kimlik']

def is_valid_candidate(candidate, context=''):
    if len(candidate) not in (10, 11):
        return False
    if candidate[0] == '0':
        return False
    ctx = context.lower()
    for kw in VKN_KEYWORDS:
        if kw in ctx:
            return True
    if len(candidate) == 11 and all(c.isdigit() for c in candidate):
        return True
    return False

def extract_from_html(html):
    candidates = []
    for m in VKN_PATTERN.finditer(html):
        v = m.group(1)
        s = max(0, m.start() - 200)
        e = min(len(html), m.end() + 200)
        if is_valid_candidate(v, html[s:e]):
            candidates.append(v)
    return list(set(candidates))

def fetch_website(url, timeout=10):
    try:
        import requests
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=timeout, verify=False)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None

def main():
    input_path = ROOT / 'data' / 'ostim' / 'firmalar_detayli.jsonl'
    output_path = ROOT / 'data' / 'ostim' / 'firmalar_vkn_ekli.jsonl'
    if not input_path.exists():
        print(f'HATA: {input_path} bulunamadi')
        return 1
    records = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    print(f'Toplam {len(records)} kayit yuklendi')
    processed = 0
    vkn_found = 0
    with open(output_path, 'w', encoding='utf-8') as out:
        for rec in records:
            processed += 1
            web = rec.get('web_sitesi')
            if web:
                if not web.startswith(('http://', 'https://')):
                    web = 'https://' + web
                html = fetch_website(web)
                if html:
                    cands = extract_from_html(html)
                    if cands:
                        rec['vergi_no'] = cands[0]
                        rec['vergi_no_kaynagi'] = 'web_footer'
                        vkn_found += 1
            out.write(json.dumps(rec, ensure_ascii=False) + '\n')
            if processed % 50 == 0:
                print(f'Ilerleme: {processed}/{len(records)}, VKN bulundu: {vkn_found}')
    print(f'Tamam! Islenen: {processed}, VKN bulundu: {vkn_found}, Cikti: {output_path}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
