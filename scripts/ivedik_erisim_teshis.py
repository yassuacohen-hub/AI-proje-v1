"""IVEDIK erisim TE$HISI (D-299) - sorunun tam olarak ne oldugunu olcer.

KAHIN sordu: "Ivedik kazima yapamiyor musun, sorun ne?"
Bu betik SAYI YOK, TEK DENEME yapar ve ham cevabi gosterir:
  1. DNS cozuluyor mu?
  2. Sunucu ne donuyor? (403 govdesi kim yazmis?)
  3. Gercek tarayici header'lari fark yaratiyor mu?
  4. Farkli Host/path denemeleri

Kullanim: python scripts/ivedik_erisim_teshis.py
"""
from __future__ import annotations

import socket
import time
from datetime import datetime

import httpx

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

#: Gercek tarayici header'lari (bot korumasi bunlari olcer)
BROWSER = {
    "User-Agent": UA,
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,*/*;q=0.8"),
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
}


def baslik(t: str) -> None:
    print()
    print("=" * 62)
    print(t)
    print("=" * 62)


def _govde_oku() -> None:
    """401 sayfasinin gercek icerigini gosterir (JS korumasini tespit)."""
    baslik("4) 401 SAYFASININ ICERIGI (bot korumasi te$hisi)")
    with httpx.Client(headers=BROWSER, timeout=20,
                      follow_redirects=True) as c:
        r = c.get("https://www.ivedikosb.org.tr/firmalar/")
    govde = r.text
    print(f"  HTTP {r.status_code} | {len(govde)} bayt")
    # Gorunur metin
    import re
    import html as html_mod
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", govde,
               flags=re.S | re.I)
    t = html_mod.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"\s+", " ", t).strip()
    print(f"  GORUNUR METIN ({len(t)} karakter): {t[:400]!r}")
    # JS ile gelen koruma ipuclari
    for desen, ad in ((r"cloudflare", "cloudflare"),
                      (r"cf-browser-verification", "cf verification"),
                      (r"challenge", "challenge"),
                      (r"Access\s*Denied|Yetkisiz|Erisim", "erisim reddi"),
                      (r"giris|login|uye|password", "giris ekrani"),
                      (r"captcha|recaptcha", "captcha")):
        if re.search(desen, govde, re.I):
            print(f"  -> ipucu: {ad}")
    # BOS MU?
    if len(t) < 40:
        print("  -> Sayfa BOS geliyor: icerik JavaScript ile yukleniyor.")


def main() -> int:
    print(f"IVEDIK ERISIM TESHISI — {datetime.now():%Y-%m-%d %H:%M:%S}")

    baslik("1) DNS")
    for h in ("www.ivedikosb.org.tr", "ivedikosb.org.tr", "ivedik.org.tr"):
        try:
            print(f"  {h:26s} -> {socket.gethostbyname(h)}")
        except Exception as e:
            print(f"  {h:26s} -> HATA ({type(e).__name__})")

    baslik("2) HTTP CEVABI (gercek tarayici header'lari)")
    for url in ("https://www.ivedikosb.org.tr/firmalar/",
                "https://www.ivedikosb.org.tr/",
                "https://www.ivedikosb.org.tr/robots.txt"):
        try:
            with httpx.Client(headers=BROWSER, timeout=20,
                              follow_redirects=True) as c:
                r = c.get(url)
            print(f"\n  {url}")
            print(f"    HTTP {r.status_code} | {len(r.text)} bayt")
            for k in ("server", "x-powered-by", "cf-ray", "x-cache",
                      "content-type", "retry-after", "x-robots-tag",
                      "www-authenticate"):
                v = r.headers.get(k)
                if v:
                    print(f"    {k:16s} {v[:60]}")
        except Exception as e:
            print(f"  {url} -> HATA {type(e).__name__}: {e}")
        time.sleep(2.0)          # nazik: kac deneme olursa olsun

    baslik("3) HTTP -> HTTPS / www / wwwsiz karsilastirma")
    for url in ("http://ivedikosb.org.tr/firmalar/",
                "https://ivedikosb.org.tr/firmalar/"):
        try:
            with httpx.Client(headers=BROWSER, timeout=20,
                              follow_redirects=True) as c:
                r = c.get(url)
            print(f"  {url:46s} -> HTTP {r.status_code}")
        except Exception as e:
            print(f"  {url:46s} -> HATA {type(e).__name__}")
        time.sleep(2.0)

    _govde_oku()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

