#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""VKN web kazima — firma sitelerinin footer/hakkimizda/iletisim sayfalarindan
Vergi No toplama (P0-3 destek: kalite skoru VKN doluluguyla artiyor).

Strateji (vkn_bulma_stratejisi.md):
  1. Merged veriden web_sitesi dolu, vergi_no'suz firmalari sec
  2. Her site icin: ana sayfa + hakkimizda/iletisim/kurumsal/kvkk yollari dene
  3. Sayfa metninden VKN adaylarini regex ile topla
  4. Turk VKN checksum dogrulamasindan gecen adaylari kabul et
  5. robots.txt kontrolu + rate limit (2 sn) + VPN kurali notu

Kullanim:
    python scripts/vkn_web_scraper.py --limit 10   # kucuk deneme
    python scripts/vkn_web_scraper.py               # web'i dolu tum kayitlar
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import urllib.robotparser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GIRDI = ROOT / "data" / "merged" / "multi_osb_merged.jsonl"
CIKTI = ROOT / "data" / "merged" / "vkn_web_bulunan.jsonl"

UA = "AnkaraB2B-Bot/1.0 (+research contact: site owner)"
AYRACI_YOLLAR = [
    "", "/hakkimizda", "/iletisim", "/kurumsal", "/kvkk", "/hakkinda",
    "/tr/hakkimizda", "/tr/iletisim", "/about", "/contact",
]

# "Vergi No : 1234567890", "V.D. Ankara 1234567890", "Vergi Dairesi: ... No: ..."
VKN_DESENLER = [
    re.compile(r"vergi\s*(?:no|numaras[ıi])\s*[:\-–]?\s*([0-9]{10})", re.IGNORECASE),
    re.compile(r"v\.?\s*d\.?\s*\.?\s*[^0-9]{0,40}([0-9]{10})", re.IGNORECASE),
    re.compile(r"vergi\s*dairesi[^0-9]{0,60}([0-9]{10})", re.IGNORECASE),
    re.compile(r"tax\s*(?:no|number|id)\s*[:\-–]?\s*([0-9]{10})", re.IGNORECASE),
]


def vkn_gecerli_mi(v: str) -> bool:
    """Turk VKN (10 hane) kontrol toplami dogrulamasi."""
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
    """Metinden checksum'u gecerli benzersiz VKN adaylarini cikarir."""
    bulunan: list[str] = []
    for desen in VKN_DESENLER:
        for m in desen.finditer(metin or ""):
            v = m.group(1)
            if vkn_gecerli_mi(v) and v not in bulunan:
                bulunan.append(v)
    return bulunan


def _get(url: str, zaman_asimi: int = 15) -> tuple[int, str]:
    """GET; (durum, metin) dondurur. VPN kurali: ag hatasinda ipucu yazilir."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "tr"})
    try:
        with urllib.request.urlopen(req, timeout=zaman_asimi) as r:
            ham = r.read()
            try:
                return r.status, ham.decode("utf-8")
            except UnicodeDecodeError:
                return r.status, ham.decode("latin-1", errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        print(f"    [AG] {url} -> {type(e).__name__}. Olasi neden: VPN. "
              "Gerekirse VPN'i kapatabilirsiniz.")
        return 0, ""


def robots_izinli_mi(domain: str, yol: str, rp_cache: dict) -> bool:
    """robots.txt'de yol engelli mi? (domain basina cache'li)"""
    rp = rp_cache.get(domain, "__yok__")
    if rp == "__yok__":
        durum, metin = _get(f"https://{domain}/robots.txt")
        if durum == 200 and metin:
            rp = urllib.robotparser.RobotFileParser()
            rp.parse(metin.splitlines())
        else:
            rp = False  # robots alinamadi -> temkinli: cekim yok
        rp_cache[domain] = rp
    if rp is False:
        return False
    try:
        return rp.can_fetch(UA, f"https://{domain}{yol or '/'}")
    except Exception:
        return False


def site_tara(domain: str, rp_cache: dict) -> list[str]:
    """Bir domain icin aday yollari tarayip gecerli VKN'leri dondurur."""
    bulunan: list[str] = []
    for yol in AYRACI_YOLLAR:
        if len(bulunan) >= 2:
            break
        if not robots_izinli_mi(domain, yol, rp_cache):
            continue
        durum, metin = _get(f"https://{domain}{yol}")
        if durum != 200 or not metin:
            durum, metin = _get(f"http://{domain}{yol}")
        if durum == 200 and metin:
            for v in vkn_ayikla(metin):
                if v not in bulunan:
                    bulunan.append(v)
            time.sleep(2)  # rate limit — nazik kazima
    return bulunan


def domain_cikar(web: str) -> str | None:
    m = re.match(r"^https?://([^/:?#]+)", (web or "").strip(), re.IGNORECASE)
    return m.group(1).lower() if m else None


def main() -> None:
    # Tek-instance kilidi
    lock = ROOT / "logs" / "vkn_web_scraper.lock"
    if lock.exists():
        print("Baska bir vkn_web_scraper.py calisiyor (lock var). Cikiliyor.",
              flush=True)
        sys.exit(0)
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(str(os.getpid()), encoding="utf-8")

    ap = argparse.ArgumentParser(description="Firma sitelerinden VKN toplama")
    ap.add_argument("--limit", type=int, default=0, help="Kac site (0=tumu)")
    args = ap.parse_args()

    if not GIRDI.exists():
        print(f"HATA: Girdi yok: {GIRDI}")
        sys.exit(1)

    adaylar: list[dict] = []
    gorulen_dom: set[str] = set()
    for ln in GIRDI.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        rec = json.loads(ln)
        if rec.get("vergi_no") or not rec.get("web_sitesi"):
            continue
        dom = domain_cikar(rec["web_sitesi"])
        if dom and dom not in gorulen_dom:
            gorulen_dom.add(dom)
            adaylar.append({"unvan": rec["unvan"], "domain": dom})
    if args.limit:
        adaylar = adaylar[: args.limit]
    print(f"VKN adayi: {len(adaylar)} site taranacak (vergi_no'suz, web'i dolu)",
          flush=True)

    sonuc: list[dict] = []
    rp_cache: dict = {}
    bulundu = robots_engelli = hata = 0
    for i, a in enumerate(adaylar):
        try:
            vknler = site_tara(a["domain"], rp_cache)
        except Exception as e:  # noqa: BLE001
            print(f"[{i}] {a['domain']} beklenmeyen hata: {type(e).__name__}: {e}",
                  flush=True)
            hata += 1
            continue
        engelli = rp_cache.get(a["domain"]) is False
        if vknler:
            bulundu += 1
            sonuc.append({**a, "vkn_bulunan": vknler})
            print(f"[{i}] BULUNDU {a['domain']}: {', '.join(vknler)}", flush=True)
        elif engelli:
            robots_engelli += 1
            print(f"[{i}] robots engelli/alinamadi: {a['domain']}", flush=True)
        else:
            print(f"[{i}] bulunamadi: {a['domain']}", flush=True)

    rapor = (
        "# VKN Web Kazima Sonuc Ozeti\n\n"
        f"- Taranan site: {len(adaylar)}\n"
        f"- VKN bulunan: {bulundu}\n"
        f"- robots engelli/alinamadi: {robots_engelli}\n"
        f"- Hata: {hata}\n"
    )
    if sonuc:
        CIKTI.write_text(
            "\n".join(json.dumps(s, ensure_ascii=False) for s in sonuc) + "\n",
            encoding="utf-8",
        )
        rapor += f"\nBulunanlar: {CIKTI}\n"
    print("\n" + rapor, flush=True)
    try:
        lock.unlink()
    except OSError:
        pass


if __name__ == "__main__":
    main()

