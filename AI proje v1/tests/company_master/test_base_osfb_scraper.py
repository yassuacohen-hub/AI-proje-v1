import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.company_master.etl.scrapers.base_osfb_scraper import BaseOsfbFirma, BaseOsfbScraper


class DummyFirma(BaseOsfbFirma):
    pass


class DummyScraper(BaseOsfbScraper):
    BASE_URL = "https://example.com"
    FIRMA_LISTE_URL = "https://example.com/firmalar/"
    USER_AGENT = "TestBot"
    WEB_BLOCKLIST = ("blocked.com",)
    FIRMA_CLASS = DummyFirma
    STATE_DIR = Path("data/dummy")
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH = STATE_DIR / ".scrape_state.json"
    OUTPUT_PATH = STATE_DIR / "firmalar.jsonl"
    log = pytest.importorskip("logging").getLogger("dummy_scraper")

    def fetch_firma_liste(self, page=1):
        return [DummyFirma(unvan="Test Firma")]

    def scrape(self, detay_al=False):
        state = self._load_state()
        toplam = state.get("total_records", 0)
        file_mode = "a" if self.OUTPUT_PATH.exists() else "w"
        with open(self.OUTPUT_PATH, file_mode, encoding="utf-8") as f:
            firmalar = self.fetch_firma_liste()
            for firma in firmalar:
                f.write(firma.to_jsonl() + "\n")
                toplam += 1
                yield firma
            state["completed_pages"] = [1]
            state["total_records"] = toplam
            self._save_state(state)


def test_base_firma_to_jsonl():
    firma = DummyFirma(unvan="Test", web_sitesi="https://example.com")
    data = firma.to_jsonl()
    assert "Test" in data
    assert "example.com" in data


def test_normalize_website():
    scraper = DummyScraper()
    assert scraper.normalize_website("example.com") == "https://example.com"
    assert scraper.normalize_website("https://example.com") == "https://example.com"
    assert scraper.normalize_website("blocked.com") is None
    assert scraper.normalize_website(None) is None
    assert scraper.normalize_website("") is None


def test_extract_vkn():
    scraper = DummyScraper()
    assert scraper.extract_vkn("1234567890") == "1234567890"
    assert scraper.extract_vkn("firma 12345678901") == "12345678901"
    assert scraper.extract_vkn("no number") is None
    assert scraper.extract_vkn(None) is None


def test_state_management():
    scraper = DummyScraper()
    state = scraper._load_state()
    assert "completed_pages" in state
    scraper._save_state({"completed_pages": [1], "total_records": 1})
    state2 = scraper._load_state()
    assert state2["completed_pages"] == [1]
    assert state2["total_records"] == 1


def test_scrape_yields_firmalar():
    scraper = DummyScraper()
    results = list(scraper.scrape(detay_al=False))
    assert len(results) == 1
    assert results[0].unvan == "Test Firma"
