"""OSTIM firma DETAY sayfasindaki alanlari olcer (D-281).

Bulgu: `ostim.org.tr/firmalar/<slug>` kalici adresler. Bu, API olmasa da
sitemap uzerinden TAM LISTE toplanmasini mumkun kiliyor.

Bu arac bir detay sayfasini acar ve hangi alanlarin bulundugunu OLER:
  unvan | adres | telefon | email | web | NACE | VKN | sicil no | ...

Kullanim: python scripts/ostim_detay_olcer.py
"""
from __future__ import annotations

import json
import pathlib
import re

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "ostim_detay_yapisi.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

#: Listede tespit edilen ilk gercek firma adresi.
ORNEK = ("https://ostim.org.tr/firmalar/"
         "2n-cam-teknolojileri-ve-yapi-sistemleri-sanayi-ltd-sti")

#: Aranacak alan etiketleri (Turkce gazete/OBY bilesenlerinden).
ALANLAR = {
    "unvan": r"(?:unvan|firma ad[iı]|şirket ad[iı])",
    "adres": r"adres",
    "telefon": r"tel(?:efon)?",
    "eposta": r"e?-?posta",
    "web": r"(?:web\s?site|internet|www\.)",
    "nace": r"\bnace\b",
    "vergi_no": r"(?:vergi\s*(?:no|number)|vkn)",
    "sicil_no": r"(?:ticaret\s+sicil|sicil\s*no|mersis)",
    "faaliyet": r"(?:faaliyet|konu)",
    "yetkili": r"(?:yetkili|ortak|temsilci)",
    "sektor": r"(?:sekt[oö]r|[uü]retim)",
}


def duz(html: str) -> str:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()


def olc() -> dict:
    o = {"ornek_url": ORNEK}
    try:
        r = httpx.get(ORNEK, timeout=30, headers={"User-Agent": UA},
                      follow_redirects=True)
        o["http"] = r.status_code
        o["bayt"] = len(r.content)
        o["son_url"] = str(r.url)
        html = r.text
        metin = duz(html)

        o["bulunan_alanlar"] = {
            ad: bool(re.search(d, html, re.I)) for ad, d in ALANLAR.items()
        }
        o["eposta_adresleri"] = sorted(
            set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", html))
        )[:5]
        o["telefonlar"] = sorted(
            set(re.findall(r"(?:\+90|0)\s?5\d{2}[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}",
                           html))
        )[:5]
        o["alan_sayisi"] = sum(1 for v in o["bulunan_alanlar"].values() if v)
        o["metin_uzunluk"] = len(metin)
        o["metin_ornegi"] = metin[:1200]
    except Exception as e:
        o["hata"] = f"{type(e).__name__}: {e}"
    return o


if __name__ == "__main__":
    res = olc()
    CIKTI.write_text(json.dumps(res, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    print("HTTP", res.get("http"), "| bayt", res.get("bayt"),
          "| alan", res.get("alan_sayisi"))
    print("BULUNAN:", [k for k, v in (res.get("bulunan_alanlar") or {}).items()
                       if v])
    print("EKSIK  :", [k for k, v in (res.get("bulunan_alanlar") or {}).items()
                       if not v])
    print("EPOSTA :", res.get("eposta_adresleri"))
    print("TEL    :", res.get("telefonlar"))
    print(CIKTI)
