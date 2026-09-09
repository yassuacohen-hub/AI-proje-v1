# -*- coding: utf-8 -*-
"""İvedik OSB scraper — BaseOsfbScraper tabanli."""
from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Any, Iterator

import requests
from bs4 import BeautifulSoup

from company_master.etl.scrapers.base_osfb_scraper import BaseOsfbFirma, BaseOsfbScraper


class IvedikFirma(BaseOsfbFirma):
    kaynak: str = "ivedikosb.org.tr"


class IvedikScraper(BaseOsfbScraper):
    BASE_URL = "https://www.ivedikosb.org.tr"
    FIRMA_LISTE_URL = f"{BASE_URL}/firmalar/"
    ROBOTS_URL = f"{BASE_URL}/robots.txt"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    RATE_LIMIT_SECONDS = 2.0
    REQUEST_TIMEOUT = 20
    WEB_BLOCKLIST = (
        "facebook.com", "twitter.com", "x.com",
        "linkedin.com", "instagram.com", "youtube.com",
    )
    STATE_DIR = Path("data/ivedik")
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH = STATE_DIR / ".scrape_state.json"
    OUTPUT_PATH = STATE_DIR / "firmalar.jsonl"
    FIRMA_CLASS = IvedikFirma
    log = logging.getLogger("ivedik_scraper")

    def fetch_firma_liste(self, page: int = 1) -> list[BaseOsfbFirma]:
        url = f"{self.FIRMA_LISTE_URL}page/{page}/" if page > 1 else self.FIRMA_LISTE_URL
        try:
            resp = requests.get(url, headers={"User-Agent": self.USER_AGENT}, timeout=self.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as exc:
            self.log.warning("Ivedik liste hatasi sayfa %d: %s", page, exc)
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        firmalar: list[BaseOsfbFirma] = []
        for card in soup.select("div.osb-list-card"):
            title_el = card.select_one("h3.osb-card-title a")
            if not title_el:
                continue
            unvan = title_el.get_text(strip=True)
            if not unvan:
                continue
            firma = self.FIRMA_CLASS(unvan=unvan)
            href = title_el.get("href", "")
            if href:
                firma.slug = href.strip("/").split("/")[-1]
            firmalar.append(firma)
        return firmalar

    def fetch_firma_detay(self, slug: str) -> dict[str, Any]:
        if not slug:
            return {}
        url = f"{self.BASE_URL}/firmalar/{slug}"
        try:
            resp = requests.get(url, headers={"User-Agent": self.USER_AGENT}, timeout=self.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as exc:
            self.log.warning("Ivedik detay hatasi %s: %s", slug, exc)
            return {}
        soup = BeautifulSoup(resp.text, "html.parser")
        detay: dict[str, Any] = {}
        container = soup.select_one("div.osb-detail-container")
        if not container:
            return detay
        full_text = container.get_text(" ", strip=True)
        vkn = self.extract_vkn(full_text)
        if vkn:
            detay["vergi_no"] = vkn
            detay["vergi_no_kaynagi"] = "ivedik_detay"
        for info in container.select(".osb-detail-contact li, .osb-detail-contact div"):
            text = info.get_text(strip=True)
            if not text:
                continue
            if "tel:" in text.lower() or re.search(r"\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}", text):
                detay["telefon"] = text
            elif "@" in text and "." in text:
                detay["email"] = text
            elif "http" in text.lower():
                detay["web_sitesi"] = text
            elif "adres" in text.lower() or any(c.isdigit() for c in text[:10]):
                detay["adres"] = text
        return detay

    def scrape(self, detay_al: bool = False) -> Iterator[BaseOsfbFirma]:
        self.log.info("BASLA İvedik OSB scraping (detayli=%s)", detay_al)
        state = self._load_state()
        toplam = state.get("total_records", 0)
        file_mode = "a" if self.OUTPUT_PATH.exists() else "w"
        with open(self.OUTPUT_PATH, file_mode, encoding="utf-8") as f:
            sayfa = 1
            while True:
                if sayfa in state.get("completed_pages", []):
                    self.log.info("Sayfa %d zaten tamamlandı, atlanıyor", sayfa)
                    sayfa += 1
                    continue
                try:
                    firmalar = self.fetch_firma_liste(sayfa)
                except NotImplementedError:
                    self.log.error("DETAYLI IMPLEMENTASYON GEREKLİ — scraper henüz aktif değil")
                    break
                except requests.RequestException as exc:
                    self.log.error("HATA sayfa %d: %s", sayfa, exc)
                    break
                if not firmalar:
                    self.log.info("Sayfa %d boş — scraping tamamlandı", sayfa)
                    break
                for firma in firmalar:
                    if detay_al and firma.slug:
                        time.sleep(self.RATE_LIMIT_SECONDS)
                        detay = self.fetch_firma_detay(firma.slug)
                        firma.web_sitesi = self.normalize_website(detay.get("web_sitesi"))
                        firma.adres = detay.get("adres")
                        firma.vergi_no = detay.get("vergi_no")
                        firma.osb_parsel = detay.get("osb_parsel")
                    f.write(firma.to_jsonl() + "\n")
                    toplam += 1
                    yield firma
                state["completed_pages"].append(sayfa)
                state["total_records"] = toplam
                self._save_state(state)
                self.log.info("Sayfa %d: %d firma (toplam: %d)", sayfa, len(firmalar), toplam)
                sayfa += 1
                time.sleep(self.RATE_LIMIT_SECONDS)
        self.log.info("BITIS İvedik OSB — %d firma yazıldı: %s", toplam, self.OUTPUT_PATH)


def scrape_ivedik(output_path: Path, detay_al: bool = False) -> Iterator[IvedikFirma]:
    scraper = IvedikScraper()
    scraper.OUTPUT_PATH = output_path
    scraper.STATE_DIR = output_path.parent
    scraper.STATE_PATH = scraper.STATE_DIR / ".scrape_state.json"
    yield from scraper.scrape(detay_al=detay_al)


if __name__ == "__main__":
    import sys
    detayli = "--detayli" in sys.argv
    if detayli:
        sys.argv.remove("--detayli")
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/ivedik/firmalar.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    for _ in scrape_ivedik(output, detay_al=detayli):
        pass
