#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""VKN web kazima v2 — gelismis scraper (requests + BeautifulSoup)."""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import requests
from bs4 import BeautifulSoup
from sqlalchemy import text
from company_master.db.connection import get_engine

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
AYRACI_YOLLAR = [
    "", "/hakkimizda", "/iletisim", "/kurumsal", "/kvkk", "/hakkinda",
    "/tr/hakkimizda", "/tr/iletisim", "/about", "/contact", "/gizlilik",
    "/gizlilik-politikasi", "/kisisel-verilerin-korunmasi", "/iletisim-formu",
    "/hakkimizda.php", "/iletisim.php", "/kurumsal.html",
]
VKN_DESENLER = [
    re.compile(r"vergi\s*(?:no|numaras[ıi])\s*[:.\-–]?\s*([0-9]{10,11})", re.IGNORECASE),
    re.compile(r"v\.?\s*d\.?\s*[^0-9]{0,40}?([0-9]{10,11})", re.IGNORECASE),
    re.compile(r"vergi\s*dairesi[^0-9]{0,60}no\s*[:.\-–]?\s*([0-9]{10,11})", re.IGNORECASE),
    re.compile(r"tax\s*(?:id|no|number)\s*[:.\-–]?\s*([0-9]{10,11})", re.IGNORECASE),
    re.compile(r"ticaret\s*sicil\s*(?:no|numaras[ıi])?\s*[:.\-–]?\s*([0-9]{10,11})", re.IGNORECASE),
    re.compile(r"\bVKN\s*[:.\-–]?\s*([0-9]{10,11})", re.IGNORECASE),
    re.compile(r"\bVD\s*[:.\-–]?\s*([0-9]{10,11})", re.IGNORECASE),
]


def vkn_gecerli_mi(v: str) -> bool:
    if len(v) != 10 or not v.isdigit():
        return False
    d = [int(c) for c in v]
    toplam = 0
    for i in range(9):
        t = (d[i] + 10 - (i + 1)) % 10
        toplam += (t * (2 ** (9 - i))) % 9
    return (10 - (toplam % 10)) % 10 == d[9]


def vkn_ayikla(metin: str) -> list[str]:
    bulunan = []
    for desen in VKN_DESENLER:
        for m in desen.finditer(metin or ""):
            v = m.group(1)
            if len(v) == 11:
                v = v[:10]
            if vkn_gecerli_mi(v) and v not in bulunan:
                bulunan.append(v)
    return bulunan


def get_page(url: str, timeout: int = 12) -> tuple[int, str]:
    try:
        r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "tr,en"},
                         timeout=timeout, allow_redirects=True)
        return r.status_code, r.text
    except requests.RequestException:
        return 0, ""


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def site_tara(domain: str) -> list[str]:
    bulunan = []
    for protokol in ["https://", "http://"]:
        for yol in AYRACI_YOLLAR:
            if len(bulunan) >= 2:
                return bulunan
            url = f"{protokol}{domain}{yol}"
            durum, html = get_page(url)
            if durum != 200 or not html:
                continue
            for v in vkn_ayikla(extract_text(html)):
                if v not in bulunan:
                    bulunan.append(v)
            time.sleep(1.5)
        if bulunan:
            break
    return bulunan


def main() -> None:
    ap = argparse.ArgumentParser(description="VKN web kazima v2")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    eng = get_engine()
    with eng.begin() as conn:
        rows = conn.execute(text("""
            SELECT company_id, trade_name, website_domain
            FROM companies
            WHERE website_domain IS NOT NULL AND website_domain <> ''
              AND (tax_number IS NULL OR tax_number = '')
            ORDER BY company_id
            LIMIT :lim
        """), {"lim": args.limit if args.limit else 500}).fetchall()

    print(f"VKN adayi: {len(rows)} site")

    sonuc = []
    bulundu = hata = 0
    for i, r in enumerate(rows):
        cid, unvan, domain = str(r[0]), r[1], r[2]
        if not domain:
            continue
        domain = domain.strip().lower()
        if domain.startswith("http"):
            domain = domain.split("//")[1].split("/")[0]
        try:
            vknler = site_tara(domain)
        except Exception:
            hata += 1
            continue
        if vknler:
            bulundu += 1
            sonuc.append({"company_id": cid, "unvan": unvan, "domain": domain, "vkn": vknler})
            print(f"[{i}] BULUNDU {domain}: {', '.join(vknler)}")
        else:
            if (i + 1) % 50 == 0:
                print(f"[{i+1}/{len(rows)}] bulunan: {bulundu}")

    out = ROOT / "data" / "merged" / "vkn_web_bulunan_v2.jsonl"
    out.write_text("\n".join(json.dumps(s, ensure_ascii=False) for s in sonuc) + "\n", encoding="utf-8")

    print(f"\n=== VKN v2 Sonuc ===")
    print(f"Taranan: {len(rows)} | Bulunan: {bulundu} | Hata: {hata}")
    print(f"Verim: {bulundu*100/max(len(rows),1):.1f}% | Cikti: {out}")


if __name__ == "__main__":
    main()