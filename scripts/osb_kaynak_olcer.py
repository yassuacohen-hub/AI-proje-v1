"""OSB (Ankara) e-Devletsiz firma verisi kaynaklarini OLcer.

GOREV (D-281): e-Devlet KULLANMADAN 14.000 firmanin sicil verisini
toplayabilecek yollari aramak. MERSİS tamamen e-Devlet'e bagli
(olculdu) → alternatifler: OSB uye listeleri, GIB VKN, acik veri.

Bu arac:
  1. Her aday kaynagi canli GET ile dener (HTTP kodu + boyut)
  2. `robots.txt` izinlerini raporlar (yasal kapı)
  3. Toplu indirme (CSV/XLSX/XML) ucu var mi arar

Kullanim: python scripts/osb_kaynak_olcer.py
"""
from __future__ import annotations

import json
import pathlib
import time

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "osb_kaynak_olcumu.json"

#: Sabit User-Agent (proje kuralı: bot taklit edilmez, kendimizi tanımlarız).
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"
)

#: e-Devletsiz olabilecek aday kaynaklar.
KAYNAKLAR = [
    ("OSTIM ana sayfa", "https://ostim.org.tr/"),
    ("OSTIM firmalar", "https://ostim.org.tr/firmalar"),
    ("OSTIM uye listesi", "https://ostim.org.tr/uye-listesi"),
    ("ATO (Ankara Ticaret Odası)", "https://www.atonet.org.tr/"),
    ("ATB (Ankara Ticaret Borsası)", "https://www.atb.org.tr/"),
    ("ASO (Ankara Sanayi Odası)", "https://www.aso.org.tr/"),
    ("GIB VKN sorgu", "https://www.gib.gov.tr/"),
    ("Ticaret Bakanlığı", "https://ticaret.gov.tr/"),
    ("MERSIS (e-Devlet kontrol)", "https://mersis.ticaret.gov.tr/"),
]


def robots_izni(alan: str) -> dict:
    """`robots.txt` var mı, içeriği ne diyor (rapor için)."""
    url = f"https://{alan}/robots.txt"
    try:
        r = httpx.get(url, timeout=20, headers={"User-Agent": UA},
                      follow_redirects=True)
        return {"url": url, "http": r.status_code,
                "icerik": r.text[:1500] if r.status_code == 200 else None}
    except Exception as e:
        return {"url": url, "hata": f"{type(e).__name__}: {e}"}


def dogrula(url: str) -> dict:
    """Tek adresi canli dener."""
    t0 = time.time()
    try:
        r = httpx.get(url, timeout=30, headers={"User-Agent": UA},
                      follow_redirects=True)
        return {
            "http": r.status_code,
            "bayt": len(r.content),
            "sure_saniye": round(time.time() - t0, 2),
            "son_url": str(r.url),
            "erisim": r.status_code == 200,
        }
    except Exception as e:
        return {"http": None, "hata": f"{type(e).__name__}: {e}",
                "erisim": False,
                "sure_saniye": round(time.time() - t0, 2)}


def main() -> dict:
    sonuclar = []
    for ad, url in KAYNAKLAR:
        o = dogrula(url)
        o["ad"] = ad
        o["url"] = url
        sonuclar.append(o)
        print(f"{ad:34s} {str(o['http']):5s} {o.get('bayt', 0):>9} bayt",
              flush=True)

    rapor = {
        "kaynaklar": sonuclar,
        "erisilebilir": [s["ad"] for s in sonuclar if s.get("erisim")],
        "robots": {},
    }
    for alan in ("ostim.org.tr", "atonet.org.tr", "aso.org.tr", "atb.org.tr"):
        rapor["robots"][alan] = robots_izni(alan)
        print("robots", alan, rapor["robots"][alan].get("http"), flush=True)

    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    CIKTI.write_text(json.dumps(rapor, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    return rapor


if __name__ == "__main__":
    r = main()
    print("\nERISILEBILIR =", r["erisilebilir"])
    print(CIKTI)
