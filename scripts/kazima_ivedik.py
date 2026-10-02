# -*- coding: utf-8 -*-
"""Ivedik OSB — LLM-less kayit kosusu (SCRAPE-002-LEMMLESS-ANKARA-OSB).

Bu bir **kaziyici degil**, kayit katmanidir:
    * Firma kaydi -> `src/company_master/etl/scrapers/ivedik_scraper.py` (kanonik)
    * Ham icerik + hash + denetim -> burasi (0050)

DIKKAT — alan adi tuzagi
    Pano kaydinda kaynak adi `ivedik.org.tr` olarak yazili; calisan site
    `www.ivedikosb.org.tr` ve DNS'te cozulmeyen `ivedik.org.tr` **ölü**.
    Brifteki adres kullanilirsa kosu hicbir sey cekmeden hata kuyruguna
    düşer. Ölçüm: `ivedik.org.tr` -> DNS yok, `www.ivedikosb.org.tr` -> HTTP 200.
    Kayit katmani ad olarak pano adini (`ivedik.org.tr`) kullanir; ag adresi
    ayridir. Ikisinin birebir ayni olmasi **beklenmez** ve karistirilmamalidir.

Kullanim
    python -X utf8 scripts/kazima_ivedik.py

Idempotens: ayni icerik ikinci kosuda yazilmaz (UNIQUE(source_url, content_hash)).

Ilgili Nodlar
    [[src/company_master/etl/scrape_kosu]] ortak kosu iskeleti
    [[src/company_master/etl/scrape_kayit]] 0050 tek yazma kapisi
    [[D-310]] kazima merkezi kaydin servisidir
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
BASE_URL = "https://www.ivedikosb.org.tr"   # calisan adres (olculdu)
KAYNAK_ADI = "ivedik.org.tr"               # pano/DB adi — ag adresi degil


def ivedik_ayikla(soup) -> dict:
    """Ivedik liste sayfasindan olculebilir alanlar.

    Olcum: 15 `div.osb-list-card`; 0 tablo.
    """
    kart = soup.select("div.osb-list-card")
    return {
        "kart_tipi": "osb-list-card" if kart else None,
        "kart_sayisi": len(kart),
        "baslik": (soup.title.get_text(strip=True) if soup.title else None),
    }


def kaynak() -> Kaynak:
    return Kaynak(
        ad=KAYNAK_ADI,
        url=f"{BASE_URL}/firmalar/",
        robots_url=f"{BASE_URL}/robots.txt",
        ayikla=ivedik_ayikla,
        not_="Ankara Ivedik OSB; 15 firma (olculdu)",
        task_id=TASK_ID,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Ivedik OSB kayit kosusu (LLM-less)")
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
    return 0 if sonuc["hata"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
