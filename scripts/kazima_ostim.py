# -*- coding: utf-8 -*-
"""OSTIM OSB — LLM-less kayit kosusu (SCRAPE-002-LEMMLESS-ANKARA-OSB).

Bu bir **kaziyici degil**, kayit katmanidir:
    * Firma kaydi  -> `src/company_master/etl/scrapers/ostim_scraper.py` (kanonik)
    * Ham icerik + hash + denetim -> burasi (0050)
Kanlik parser burada YOK; sekiz kez tekrarlanmasina gerek yok (D-211).

Kullanim
    python -X utf8 scripts/kazima_ostim.py
    python -X utf8 scripts/kazima_ostim.py --detay   (rapor ayrintisi)

Idempotens: ayni icerik ikinci kosuda yazilmaz (UNIQUE(source_url, content_hash)).

Ilgili Nodlar
    [[src/company_master/etl/scrape_kosu]] ortak kosu iskeleti
    [[src/company_master/etl/scrape_kayit]] 0050 tek yazma kapisi
    [[D-310]] kazima merkezi kaydin servisidir
    [[D-261]] content_hash UNIQUE dedup
    [[plans/brief_utku_SCRAPE-002-LEMMLESS-ANKARA-OSB]] gorev brifi
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from company_master.etl.scrape_kosu import Kaynak, kosu  # noqa: E402

TASK_ID = "SCRAPE-002-LEMMLESS-ANKARA-OSB"
BASE_URL = "https://ostim.org.tr"

# OSTIM'de 0 <table> ve 0 tr.data olculdu; firma adetleri kart degil
# detay linklerinden gelir: div.col-lg-4.mb-3 icinde a[href^='/firmalar/'].
DETAY_LINK = "a[href^='/firmalar/']"


def ostim_ayikla(soup) -> dict:
    """OSTIM liste sayfasindan olculebilir alanlar.

    Brief'teki "bilinen CSS secicisi" iddiasi olcumle dogrulanmadi; burada
    yalnizca **olculmus** sayilar yazilir ve hangi sayinin nereden geldigi
    `kart_tipi` ile bildirilir (D-245: doluluk gecerlilik degildir).
    """
    kart = soup.select("div.col-lg-4.mb-3")
    linkler = soup.select(DETAY_LINK)
    return {
        "kart_tipi": "col-lg-4.mb-3",
        "kart_sayisi": len(kart),
        "detay_link_sayisi": len(linkler),
        "baslik": (soup.title.get_text(strip=True) if soup.title else None),
    }


def kaynak() -> Kaynak:
    return Kaynak(
        ad="ostim.org.tr",
        url=f"{BASE_URL}/firmalar",
        robots_url=f"{BASE_URL}/robots.txt",
        ayikla=ostim_ayikla,
        not_="Ankara OSB; 15 kaynakli en buyuk liste",
        task_id=TASK_ID,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="OSTIM OSB kayit kosusu (LLM-less)")
    p.add_argument("--detay", action="store_true", help="alanlari yazdir")
    p.add_argument("--log", default="INFO", help="log seviyesi")
    a = p.parse_args()
    logging.basicConfig(
        level=getattr(logging, a.log.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    sonuc = kosu(kaynak())
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    if a.detay and sonuc.get("alanlar"):
        print(json.dumps(sonuc["alanlar"], ensure_ascii=False, indent=2))
    # 0 = basarili (yazilsa da atlanisa da), 1 = izin/hata
    return 0 if sonuc["hata"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
