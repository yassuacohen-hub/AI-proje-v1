"""OSTIM/ATO uye listelerinin VERI YAPISINI olcer (D-281).

Yasal kapi gecti (robots.txt izin veriyor). Simdi asil soru:
  1. Sayfada gercekten firma KAYDI var mi?
  2. Alanlar neler (unvan, adres, NACE, VKN, sicil no)?
  3. Sayfalama var mi? Toplam kac firma?
  4. Toplu indirme (CSV/XLSX/API) ucu var mi?

Bu olcum YAPILMADAN "14.000 firma toplanir" denmez.
"""
from __future__ import annotations

import json
import pathlib
import re

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "osb_veri_yapisi.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

#: Uye/firma listesi olasi aday sayfalar.
HEDEFLER = [
    ("OSTIM firmalar", "https://ostim.org.tr/firmalar"),
    ("ATO uye sirketleri", "https://www.atonet.org.tr/uye-sirketler"),
    ("ATO uye listesi", "https://www.atonet.org.tr/uyeler"),
    ("ASO uye listesi", "https://www.aso.org.tr/uyeler"),
]


def duz(html: str) -> str:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()


def olc(ad: str, url: str) -> dict:
    o = {"ad": ad, "url": url}
    try:
        r = httpx.get(url, timeout=30, headers={"User-Agent": UA},
                      follow_redirects=True)
        o["http"] = r.status_code
        o["bayt"] = len(r.content)
        if r.status_code != 200:
            o["erisim"] = False
            return o
        o["erisim"] = True
        html = r.text

        # Firma kaydi isareti: tablo satiri / kart / unvan kaliplari
        o["tablo_satir"] = len(re.findall(r"<tr[^>]*>", html, re.I))
        o["kart_adedi"] = len(
            re.findall(r'class="[^"]*(?:kart|card|uy|firma)[^"]*"', html, re.I)
        )
        o["sirket_unvani_adi"] = html.lower().count("a.ş")
        o["ticaret_sicil_adi"] = len(
            re.findall(r"(?:ticaret\s+sicil|sicil\s+no|mersis)", html, re.I)
        )
        o["vergi_no_adi"] = len(
            re.findall(r"(?:vergi\s+no|vkn|tax\s+no)", html, re.I)
        )
        o["nace_adi"] = len(re.findall(r"\bnace\b", html, re.I))

        # Sayfalama
        o["sayfalama"] = len(
            re.findall(r"(?:page=|p=\d|sayfa|PageNumber)", html, re.I)
        )
        # Toplu indirme
        o["csv_xlsx_xls"] = sorted(
            set(
                re.findall(
                    r'href="([^"]+\.(?:csv|xlsx?|xml|json))"', html, re.I
                )
            )
        )[:8]

        metin = duz(html)
        o["metin_uzunluk"] = len(metin)
        # Ornek kayitlar: unvan benzeri satir
        o["ornek_satirlar"] = [
            s[:130]
            for s in re.findall(r"[^|]{15,130}", metin)
            if re.search(r"(?:A\.Ş|LTD|ŞTİ|LİMİT|ANONİM|SANAYİ|DİŞ|İHRACAT)", s)
        ][:6]
        o["toplam_ilan_adi"] = len(
            re.findall(r"\d[\d.]*\s*(?:firma|üye|member|kayıt)", metin, re.I)
        )
    except Exception as e:
        o["hata"] = f"{type(e).__name__}: {e}"
        o["erisim"] = False
    return o


if __name__ == "__main__":
    sonuclar = [olc(a, u) for a, u in HEDEFLER]
    CIKTI.write_text(json.dumps(sonuclar, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    for s in sonuclar:
        print(
            f"{s['ad']:24s} http={str(s.get('http')):5s} "
            f"tr={s.get('tablo_satir','?'):>5} s.no={s.get('ticaret_sicil_adi','?'):>3} "
            f"v.no={s.get('vergi_no_adi','?'):>3} nace={s.get('nace_adi','?'):>3} "
            f"sayfa={s.get('sayfalama','?')}"
        )
    print(CIKTI)
