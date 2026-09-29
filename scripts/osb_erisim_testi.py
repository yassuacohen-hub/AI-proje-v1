"""Eksik 4 OSB'nin kaynak sitelerine erisim testi (SALT OKUNUR).

KAHIN 2026-09-29: "eksik 4 OSB'de bitir, hepsini topla".
Once erisim olculur; olcum olmadan tarama baslatilmaz (P-1..P-10).
"""
from __future__ import annotations

import csv
import pathlib

CSV = pathlib.Path(r"C:\Huginn Data Projesi\workflows\huginn-muninn"
                   r"\ankara_osb_listesi.csv")
ANAHTARLAR = ("Polatl", "kümcü", "Elmada", "erefliko")


def main() -> None:
    import httpx
    satirlar = list(csv.DictReader(CSV.open(encoding="utf-8-sig")))
    baslik = list(satirlar[0])
    ad_k, web_k = baslik[0], baslik[4]
    UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    print("=" * 70)
    print("EKSIK 4 OSB — KAYNAK SITE ERISIM TESTI (salt okunur)")
    print("=" * 70)
    for r in satirlar:
        ad = r[ad_k]
        if not any(k in ad for k in ANAHTARLAR):
            continue
        url = r[web_k]
        print(f"\n{ad}")
        print(f"  {url}")
        try:
            with httpx.Client(headers={"User-Agent": UA},
                              timeout=20, follow_redirects=True) as c:
                cevap = c.get(url)
                print(f"  HTTP {cevap.status_code} | "
                      f"{len(cevap.text)} bayt | "
                      f"son: {str(cevap.url)[:50]}")
        except Exception as e:
            print(f"  HATA: {type(e).__name__}: {str(e)[:70]}")


if __name__ == "__main__":
    main()
