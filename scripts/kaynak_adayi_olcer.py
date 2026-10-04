# -*- coding: utf-8 -*-
"""Yeni kaynak adayi kesfi — canli GET, KISA timeout (D-260: olcum).

Neden: TOBB2B verisi 21068'te bitti (500 Id olcumunde 0 teklif). Yeni kaynak
gerekiyor. Bu arac yalnizca ERISILEBILIRLIK olcer — toplu indirme YAPMAZ
(hir kaynak icin tek istek). Aktif tarama brif yasagi: bu arac sadece kapiyi
olcer, icerik cekmez.

Kurallar: R1 (rate-limit), D-86 (tek seferlik komut, dosya), D-245 (kod degil,
olculmus cikti).
"""
from __future__ import annotations

import pathlib
import re
import sys

import httpx

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

#: (ad, url, aranacak anahtar_kelimeler)
ADAYLAR = [
    ("ATO uye bilgileri", "https://www.atonet.org.tr/uye-bilgileri",
     ("uye", "firma", "sicil", "unvan", "vkn")),
    ("ATO istatistik", "https://www.atonet.org.tr/istatistik",
     ("uye", "firma", "sicil", "unvan")),
    ("ASO uye listesi", "https://www.aso.org.tr/uye-listesi",
     ("uye", "firma", "sicil", "unvan")),
    ("Ticaret Bakanligi uye", "https://ticaret.gov.tr/",
     ("firma", "sicil", "unvan", "liste")),
]

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "kaynak_adayi_olcumu.json"


def olc() -> list[dict]:
    sonuc = []
    with httpx.Client(headers={"User-Agent": UA}, timeout=12,
                      follow_redirects=True) as c:
        for ad, url, kelimeler in ADAYLAR:
            kayit: dict = {"ad": ad, "url": url}
            try:
                r = c.get(url)
                # httpx'te HTTP kodu `status_code` (urllib'nin `getcode()`'i YOK)
                kayit["http"] = r.status_code
                kayit["bayt"] = len(r.content)
                metin = re.sub(r"<[^>]+>", " ", r.text)
                metin = re.sub(r"\s+", " ", metin)
                kucuk = metin.lower()
                kayit["anahtar_sayi"] = {k: kucuk.count(k) for k in kelimeler}
                # Linklerden aday uclar
                linkler = sorted(set(re.findall(r'href=["\']([^"\']+)["\']', r.text)))
                kayit["link_sayi"] = len(linkler)
                kayit["linkler"] = [
                    x for x in linkler
                    if any(k in x.lower() for k in
                           ("uye", "firma", "liste", "istat", "sorgu", "arama"))
                ][:12]
            except Exception as exc:  # noqa: BLE001
                kayit["hata"] = f"{type(exc).__name__}: {exc}"[:120]
            sonuc.append(kayit)
            print(f"  {ad:24s} http={kayit.get('http')} "
                  f"bayt={kayit.get('bayt')} hata={kayit.get('hata', '-')}")
    return sonuc


def main() -> int:
    print("=" * 68)
    print("YENI KAYNAK ADAYI KESFI — sadece erisilebilirlik olcumu")
    print("=" * 68)
    veri = olc()
    CIKTI.write_text(__import__("json").dumps(veri, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    print(f"\nYAZILDI: {CIKTI.relative_to(KOK).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
