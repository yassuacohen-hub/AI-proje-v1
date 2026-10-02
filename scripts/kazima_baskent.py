# -*- coding: utf-8 -*-
"""Baskent OSB — LLM-less kayit kosusu (SCRAPE-002-LEMMLESS-ANKARA-OSB).

Bu bir **kaziyici degil**, kayit katmanidir:
    * Firma kaydi -> `src/company_master/etl/scrapers/baskent_scraper.py` (kanonik)
    * Ham icerik + hash + denetim -> burasi (0050)

OLCILMIS GERCEK — bu kaynak CALISMIYOR
    `baskentosb.org.tr` ve `www.baskentosb.org.tr` DNS'ten cozulmuyor
    (Resolve-DnsName: name does not exist). Bu yuzden:
      * Python `requests` -> `ConnectionError` (DNS)
      * Merkezi router  -> `allowed=False`, sebep "robots.txt alinamadi"
        (robotparser erisilemeyen domain icin **varsayilan RED** verir)
    Buradaki kosu **hata uretmez**: kural uygulanir, izin reddi
    `scrape_errors`'a yazilir ve surec `hata: 1` ile **basarili** biter.
    Bu dogru davranistir — ulasilamayan kaynak sessizce gecmez (D-310/4).

    Bu dosya bir sonraki alan adinin bulunmasi halinde **degistirilmez**;
    yalniz `BASE_URL` guncellenir. Adresi elle bulmak yerine, kayit
    `scrape_errors`a yazildigi icin ilk denemede kanit birikir.

Kullanim
    python -X utf8 scripts/kazima_baskent.py

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
BASE_URL = "https://baskentosb.org.tr"   # olcum: DNS cozumlenmiyor


def baskent_ayikla(soup) -> dict:
    """Baskent liste sayfasindan olculebilir alanlar.

    Sayfa kalibi **olculmedi** (site erisilemiyor); varsayilan ayiklayici
    kullanilir. Donen `kart_tipi: None` "yapı bilinmiyor" demektir —
    sifiri "0 firma" gibi okutmamak icin acikca yazilir (D-245).
    """
    kart = soup.select("div.osb-list-card") or soup.select("div.col-lg-4.mb-3")
    return {
        "kart_tipi": "osb-list-card" if kart else None,
        "kart_sayisi": len(kart),
        "baslik": (soup.title.get_text(strip=True) if soup.title else None),
    }


def kaynak() -> Kaynak:
    return Kaynak(
        ad="baskentosb.org.tr",
        url=f"{BASE_URL}/firmalar",
        robots_url=f"{BASE_URL}/robots.txt",
        ayikla=baskent_ayikla,
        not_="Ankara Baskent OSB; DNS cozumlenmiyor (olculdu 2026-10-02)",
        task_id=TASK_ID,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Baskent OSB kayit kosusu (LLM-less)")
    p.add_argument("--detay", action="store_true", help="alanlari yazdir")
    p.add_argument("--log", default="INFO", help="log seviyesi")
    a = p.parse_args()
    logging.basicConfig(
        level=getattr(logging, a.log.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    sonuc = kosu(kaynak())
    # Ulasilamayan kaynak hata degildir: kural uygulandi, iz yazildi.
    # Cikis kodu 0 — aksi halde zincir kosulmamis bir kaynak yuzunden kirilir.
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
