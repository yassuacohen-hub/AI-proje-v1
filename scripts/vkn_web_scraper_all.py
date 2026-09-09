#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tum OSB kaynaklari icin VKN kazima.

Ivedik ve Baskent scraper ciktilarindan web sitesi VKN cikarir.
Format: data/{osb}/firmalar.jsonl
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

VKN_PATTERN = re.compile(r'\b(\d{10,11})\b')
VKN_KEYWORDS = ['vergi no', 'vkn', 'vergi dairesi', 'tax number', 'tax id']
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

SOURCES = [
    ('ostim', ROOT / 'data' / 'ostim' / 'firmalar_detayli.jsonl'),
    ('ivedik', ROOT / 'data' / 'ivedik' / 'firmalar.jsonl'),
    ('baskent', ROOT / 'data' / 'baskent' / 'firmalar.jsonl'),
]


def is_valid_vkn(candidate: str, context: str) -> bool:
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


def extract_vkn_from_html(html: str) -> str | None:
    for m in VKN_PATTERN.finditer(html):
        v = m.group(1)
        s = max(0, m.start() - 200)
        e = min(len(html), m.end() + 200)
        if is_valid_vkn(v, html[s:e]):
            return v
    return None


def fetch_website(url: str, timeout: int = 15) -> str | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, verify=False)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None


def process_source(name: str, path: Path) -> int:
    if not path.exists():
        print(f"{name}: dosya yok")
        return 0

    records: list[dict[str, Any]] = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"{name}: {len(records)} kayit")
    found = 0
    for i, rec in enumerate(records):
        if rec.get('vergi_no'):
            continue
        web = rec.get('web_sitesi')
        if not web:
            continue
        if not web.startswith(('http://', 'https://')):
            web = 'https://' + web
        html = fetch_website(web)
        if html:
            vkn = extract_vkn_from_html(html)
            if vkn:
                rec['vergi_no'] = vkn
                rec['vergi_no_kaynagi'] = 'web_kazima'
                found += 1
        time.sleep(0.5)

    with open(path, 'w', encoding='utf-8') as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')

    print(f"{name}: VKN bulundu {found}/{len(records)}")
    return found


def main() -> int:
    total_found = 0
    for name, path in SOURCES:
        total_found += process_source(name, path)
    print(f"Toplam VKN bulundu: {total_found}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
