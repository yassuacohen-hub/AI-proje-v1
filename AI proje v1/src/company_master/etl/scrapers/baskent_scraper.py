# -*- coding: utf-8 -*-
"""Başkent OSB scraper — BaseOsfbScraper tabanli."""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Iterator

import requests
from bs4 import BeautifulSoup

from company_master.etl.scrapers.base_osfb_scraper import BaseOsfbFirma, BaseOsfbScraper


class BaskentFirma(BaseOsfbFirma):
    kaynak: str = "baskentosb.org"


class BaskentScraper(BaseOsfbScraper):
    BASE_URL = "https://www.baskentosb.org"
    FIRMA_LISTE_URL = f"{BASE_URL}/tr/firma-listesi/"
    ROBOTS_URL = f"{BASE_URL}/robots.txt"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    RATE_LIMIT_SECONDS = 1.0
    REQUEST_TIMEOUT = 20
    WEB_BLOCKLIST = (
        "facebook.com", "twitter.com", "x.com",
        "linkedin.com", "instagram.com", "youtube.com",
    )
    STATE_DIR = Path("data/baskent")
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH = STATE_DIR / ".scrape_state.json"
    OUTPUT_PATH = STATE_DIR / "firmalar.jsonl"
    FIRMA_CLASS = BaskentFirma
    log = logging.getLogger("baskent_scraper")

    def fetch_firma_liste(self, page: int = 1) -> list[BaseOsfbFirma]:
        url = self.FIRMA_LISTE_URL
        try:
            resp = requests.get(url, headers={"User-Agent": self.USER_AGENT}, timeout=self.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as exc:
            self.log.warning("Baskent liste hatasi: %s", exc)
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        firmalar: list[BaseOsfbFirma] = []
        for item in soup.find_all("div", class_=__import__("re").compile(r"gdlr-core-course-item")):
            name_el = item.select_one("h3.gdlr-core-course-item-title")
            if not name_el:
                continue
            unvan = name_el.get_text(strip=True)
            if not unvan:
                continue
            firma = self.FIRMA_CLASS(unvan=unvan)
            for info in item.select(".gdlr-core-course-item-info"):
                icon = info.select_one("i.fa")
                tail = info.select_one(".gdlr-core-tail")
                text = tail.get_text(strip=True) if tail else info.get_text(strip=True)
                if not text:
                    continue
                icon_class = icon.get("class", []) if icon else []
                if "fa-map-marker" in icon_class:
                    firma.adres = text
                elif "fa-globe" in icon_class:
                    link = tail.select_one("a[href^=http]") if tail else None
                    firma.web_sitesi = self.normalize_website(link.get("href") if link else text)
                elif "fa-building" in icon_class:
                    firma.sektor = text
                elif "fa-asterisk" in icon_class:
                    if not firma.sektor:
                        firma.sektor = text
            firmalar.append(firma)
        return firmalar

    def fetch_firma_detay(self, slug: str) -> dict[str, Any]:
        return {}

    def scrape(self, detay_al: bool = False) -> Iterator[BaseOsfbFirma]:
        self.log.info("BASLA Baskent OSB scraping (detayli=%s)", detay_al)
        state = self._load_state()
        toplam = state.get("total_records", 0)
        file_mode = "a" if self.OUTPUT_PATH.exists() else "w"
        with open(self.OUTPUT_PATH, file_mode, encoding="utf-8") as f:
            self.log.info("Baskent firm listesi cekiliyor...")
            firmalar = self.fetch_firma_liste()
            if not firmalar:
                self.log.warning("Baskent firma listesi bos — scraping tamamlandi")
                return
            for firma in firmalar:
                f.write(firma.to_jsonl() + "\n")
                toplam += 1
                yield firma
            state["completed_pages"] = [1]
            state["total_records"] = toplam
            self._save_state(state)
            self.log.info("BITIS Baskent OSB — %d firma yazildi: %s", toplam, self.OUTPUT_PATH)


def scrape_baskent(output_path: Path, detay_al: bool = False) -> Iterator[BaskentFirma]:
    scraper = BaskentScraper()
    scraper.OUTPUT_PATH = output_path
    scraper.STATE_DIR = output_path.parent
    scraper.STATE_PATH = scraper.STATE_DIR / ".scrape_state.json"
    yield from scraper.scrape(detay_al=detay_al)


if __name__ == "__main__":
    import sys
    detayli = "--detayli" in sys.argv
    if detayli:
        sys.argv.remove("--detayli")
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/baskent/firmalar.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    for _ in scrape_baskent(output, detay_al=detayli):
        pass
