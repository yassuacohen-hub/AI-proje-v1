"""TEKNIK KESIF — iki yeni kaynak site (SALT OKUNUR, yazma yok).

KAHIN 2026-09-29: "sanayi.org.tr ve tobb2b.org.tr bu iki siteyi incele,
sistemimizde neler yapilabilir, satis firsati vs, anlamli bir sey cikar mi"

POLITIKA: burada yalnizca KOK SAYFA ve acik uc noktalari okunur.
Toplu tarama YAPILMAZ (izin kapisi gecerli).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.parse as up

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

HEDEFLER = [
    ("sanayi_veri_tabani",
     "https://sanayi.org.tr/#/sanayi-veri-tabani"),
    ("sanayi_ana", "https://sanayi.org.tr/"),
    ("tobb2b", "https://www.tobb2b.org.tr/index.php"),
]

KOK = pathlib.Path(__file__).resolve().parents[1]
RAPOR = KOK / "data" / "_tmp" / "kaynak_kesif.json"


def duz(html: str) -> str:
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&quot;", '"'),
                 ("&#39;", "'"), ("&#8211;", "-")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def main() -> None:
    import httpx
    bulgu: dict = {}
    for ad, url in HEDEFLER:
        print("\n" + "=" * 68)
        print(f"{ad} | {url}")
        print("=" * 68)
        kayit: dict = {"url": url}
        try:
            with httpx.Client(headers={"User-Agent": UA}, timeout=25,
                              follow_redirects=True) as c:
                r = c.get(url)
                html = r.text
                kayit["http"] = r.status_code
                kayit["bayt"] = len(html)
                kayit["son_url"] = str(r.url)
                kok = up.urljoin(str(r.url), "/robots.txt")
                try:
                    rr = c.get(kok, timeout=10)
                    kayit["robots_http"] = rr.status_code
                    dis = [x.split(":", 1)[1].strip()
                           for x in rr.text.splitlines()
                           if x.lower().startswith("disallow")
                           and x.split(":", 1)[1].strip()]
                    kayit["robots_disallow"] = dis[:8]
                except Exception as e:
                    kayit["robots"] = f"hata {type(e).__name__}"
        except Exception as e:
            kayit["hata"] = f"{type(e).__name__}: {str(e)[:60]}"
            print(f"  ERISIM YOK: {kayit['hata']}")
            bulgu[ad] = kayit
            continue

        print(f"  HTTP {kayit['http']} | {kayit['bayt']} bayt")
        print(f"  son: {kayit['son_url'][:66]}")
        print(f"  robots: HTTP {kayit.get('robots_http')} | "
              f"disallow: {kayit.get('robots_disallow')}")

        # SPA mi? (#/ ile baslayan route)
        print(f"  SPA (#/ route): {'#/' in url}")
        # API ucu ipuclari
        api = sorted(set(re.findall(
            r'["\']([^"\']{6,110}(?:api|/api|rest|graphql)[^"\']*)["\']',
            html, re.I)))
        print(f"  API ipucu: {len(api)}")
        for a in api[:4]:
            print(f"      {a[:66]}")
        kayit["api_ipuclari"] = api[:10]

        # veri tabani / uye / firma linkleri
        link = re.findall(r'href="([^"]+)"', html)
        ilgi = [x for x in set(link) if re.search(
            r"(veri|taban|firma|uye|member|osb|sektor|ürün|urun|"
            r"ihracat|tedarik)", x, re.I)]
        print(f"  ilgili link: {len(ilgi)}")
        for x in sorted(ilgi)[:6]:
            print(f"      {x[:66]}")
        kayit["ilgili_link"] = sorted(ilgi)[:20]

        # gorunen metin
        m = duz(html)
        kayit["metin_ornegi"] = m[:600]
        print(f"  metin: {len(m)} karakter")
        print(f"  ilk 260: {m[:260]}")
        bulgu[ad] = kayit

    RAPOR.parent.mkdir(parents=True, exist_ok=True)
    RAPOR.write_text(json.dumps(bulgu, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    print(f"\nRapor: {RAPOR}")


if __name__ == "__main__":
    main()
