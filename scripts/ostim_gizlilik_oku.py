"""D-282: OSTIM Gizlilik Politikasi'nin UYGUNLUK KURALLARINI cikarir.

Neden: 8.473 uye listesinde unvan/adres/telefon/e-posta YAYIMLANMIS
durumda. Ticari kullanim (veri satisi, scraping) bu kurallara tabidir.

Bu arac metni bolumlere ayirip her bolumun basligini + ilk cumlelerini
doner; insan karar verebilsin diye ALINTILANIR (ozet degil).

Kullanim: python scripts/ostim_gizlilik_oku.py
"""
from __future__ import annotations

import json
import pathlib
import re

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "ostim_gizlilik_bolumler.json"
URL = "https://ostim.org.tr/kurumsal/gizlilik-politikasi"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

#: Aranan uygunluk basliklari (buyuk harfli basliklar).
HEDEF_BASLIK = re.compile(
    r"([ÇĞİÖŞÜçğıöşüA-Z][A-ZÇĞİÖŞÜ çğıöşüa-z0-9/()\-]{8,90})"
)


def duz(html: str) -> str:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", "\n", t)
    return t


def temizle(html: str) -> str:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", t).strip()


if __name__ == "__main__":
    r = httpx.get(URL, timeout=30, headers={"User-Agent": UA},
                  follow_redirects=True)
    html = r.text
    # Blok basligi + icerik
    bloklar = re.findall(r"<h[1-6][^>]*>(.*?)</h[1-6]>(.*?)(?=<h[1-6]|$)",
                         html, re.S | re.I)
    cikti = []
    for bas_html, govde_html in bloklar:
        bas = temizle(bas_html)
        if not bas or len(bas) < 5:
            continue
        govde = temizle(govde_html)
        cikti.append({
            "baslik": bas,
            "uzunluk": len(govde),
            "ilk_cumleler": [s.strip()[:300]
                             for s in re.split(r"(?<=\.)\s+", govde)[:4] if s.strip()],
            "tam_metin": govde,
        })

    sonuc = {
        "url": URL,
        "http": r.status_code,
        "metin_uzunluk": len(temizle(html)),
        "bolum_sayisi": len(cikti),
        "bolumler": cikti,
    }
    CIKTI.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    print("BOLUM SAYISI =", len(cikti))
    for b in cikti:
        print("  -", b["baslik"][:80], "|", b["uzunluk"], "karakter")
    print(CIKTI)
