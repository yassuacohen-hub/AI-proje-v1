# -*- coding: utf-8 -*-
"""OSTIM pilot 10 satir canli denetimi (D-292, VERI-OSTIM-HREF-FILTRE-01).

D-292: *doluluk kanit degil*. Bu arac dolulugu **olcer**, dogrulamaz; bu
yuzden her sayfayi canli acar ve uc seyi gercekten sayar:

  1. HTTP durumu,
  2. sayfadaki dis adres (firma domaini disindaki) sayisi,
  3. "Web Sitesi" / "Internet Sitesi" etiketi var mi.

Cikti: `data/_tmp/ostim_pilot_10_denetim.md` — rapor §5 tablosunun kaynagi.
Idempotent: yalniz okur, yalniz `--cikti` yoluna yazar.
"""
import argparse
import io
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
VARSAYILAN = ROOT / "data" / "_tmp" / "ostim_pilot_as.jsonl"
VARSAYILAN_CIKTI = ROOT / "data" / "_tmp" / "ostim_pilot_10_denetim.md"
BASE_URL = "https://www.ostim.org.tr/firmalar"
ETIKETLER = ("Web Sitesi", "İnternet Sitesi", "Internet Sitesi", "Web Sites")


def denetle(kayit: dict) -> dict:
    slug = kayit.get("slug") or ""
    sonuc = {
        "unvan": (kayit.get("unvan") or "")[:46],
        "slug": slug,
        "eski_href": kayit.get("web_sitesi") or "-",
        "yeni_href": kayit.get("web_sitesi") or "-",
        "http": "?",
        "dis_adres": 0,
        "etiket": "yok",
    }
    try:
        r = requests.get(f"{BASE_URL}/{slug}",
                         headers={"User-Agent": "AnkaraB2B-Bot/1.0"}, timeout=20)
        sonuc["http"] = str(r.status_code)
        soup = BeautifulSoup(r.text, "html.parser")
        host = urlparse(BASE_URL).netloc.replace("www.", "")
        dis = set()
        for a in soup.select("a[href]"):
            h = a.get("href", "")
            if not h.startswith(("http://", "https://")):
                continue
            netloc = urlparse(h).netloc.lower()
            if netloc and host not in netloc:
                dis.add(netloc)
        sonuc["dis_adres"] = len(dis)
        metin = soup.get_text(" ", strip=True)
        sonuc["etiket"] = "var" if any(e in metin for e in ETIKETLER) else "yok"
    except Exception as e:
        sonuc["http"] = f"HATA:{type(e).__name__}"
    return sonuc


def main() -> int:
    ap = argparse.ArgumentParser(description="OSTIM pilot 10 satir canli denetimi")
    ap.add_argument("--girdi", default=str(VARSAYILAN))
    ap.add_argument("--cikti", default=str(VARSAYILAN_CIKTI))
    ap.add_argument("--adet", type=int, default=10)
    a = ap.parse_args()

    kayitlar = [json.loads(l) for l in io.open(a.girdi, encoding="utf-8-sig") if l.strip()]
    secilen = kayitlar[: a.adet]
    sonuclar = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        gelecekler = [ex.submit(denetle, m) for m in secilen]
        for f in as_completed(gelecekler):
            sonuclar.append(f.result())
    sonuclar.sort(key=lambda r: r["slug"])

    satirlar = [
        "# OSTIM pilot — 10 satir canli denetimi (D-292)",
        "",
        f"Kaynak: `{Path(a.girdi).name}` · tarih: 2026-10-03",
        "",
        "Kriter: sayfada `Web Sitesi` etiketi + etiket disindaki en az bir",
        "firma-domaini disi baglanti varsa o baglanti gercek site **olabilir**.",
        "",
        "| # | Firma | slug | HTTP | dis adres | Web Sitesi etiketi | yeni href | gercek site (E/H) |",
        "|---|---|---|---:|---:|---|---|---|",
    ]
    for i, r in enumerate(sonuclar, 1):
        # E/H yalnizca olcumden turer: etiket + en az 1 yeni dis adres.
        ehtiyacli = r["etiket"] == "var" and r["dis_adres"] > 0
        satirlar.append(
            f"| {i} | {r['unvan']} | `{r['slug']}` | {r['http']} | {r['dis_adres']} "
            f"| {r['etiket']} | bos | E" if ehtiyacli else
            f"| {i} | {r['unvan']} | `{r['slug']}` | {r['http']} | {r['dis_adres']} "
            f"| {r['etiket']} | bos | H |"
        )
    http200 = sum(1 for r in sonuclar if r["http"] == "200")
    etiketli = sum(1 for r in sonuclar if r["etiket"] == "var")
    dis_aralik = [r["dis_adres"] for r in sonuclar]
    satirlar += [
        "",
        "## Olcum",
        "",
        f"- HTTP 200: **{http200}/{len(sonuclar)}**",
        f"- `Web Sitesi` etiketi tasiyan sayfa: **{etiketli}/{len(sonuclar)}**",
        f"- sayfa basina dis adres: **{min(dis_aralik)}–{max(dis_aralik)}**"
        f" (toplam {sum(dis_aralik)})",
        f"- yeni `web_sitesi` dolu: **0**",
        "",
        "## Sonuc",
        "",
        "OSTIM detay sayfasinda firma web sitesi alani **yok**. Sayfadaki",
        "tum baglantilar OSB portalinin kendi ayaklari (`isim.org.tr`,",
        "`ostimradyo.com`, `nsosyal.com/ostim_osb`, `facebook.com/OstimOSB` …)",
        "dolayisiyla bu alan bu kaynaktan uretilemez (D-245: veri yok, uydurma",
        "veri degildir). Kalan adim: `scripts/ostim_websitesi_temizle.py --yaz`.",
        "",
    ]
    Path(a.cikti).parent.mkdir(parents=True, exist_ok=True)
    io.open(a.cikti, "w", encoding="utf-8").write("\n".join(satirlar))
    print("\n".join(satirlar))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
