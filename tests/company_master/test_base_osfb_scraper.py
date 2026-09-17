import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.company_master.etl.scrapers.base_osfb_scraper import BaseOsfbFirma, BaseOsfbScraper


class DummyFirma(BaseOsfbFirma):
    pass


class DummyScraper(BaseOsfbScraper):
    """TEST-ISO-03: STATE_DIR/OUTPUT_PATH import anında SABİTLENMEZ.

    Regresyon: önceki sürümde ``STATE_DIR = Path("data/dummy")`` sınıf
    gövdesinde tanımlıydı ve modül import edilirken gerçek repo dizinini
    oluşturuyor; ``scrape()`` append moduyla her test koşusunda
    ``data/dummy/firmalar.jsonl``'e (git'te takip edilen dummy veri) bir
    "Test Firma" satırı ekliyordu (17.09.2026 bulgusu: +24 satır/gün).
    Artık tüm yazma hedefleri ``tmp_path``'e bağlanır (aşağıdaki fixture).
    """

    BASE_URL = "https://example.com"
    FIRMA_LISTE_URL = "https://example.com/firmalar/"
    USER_AGENT = "TestBot"
    WEB_BLOCKLIST = ("blocked.com",)
    FIRMA_CLASS = DummyFirma
    STATE_DIR = Path(".")
    STATE_PATH = Path(".scrape_state.json")
    OUTPUT_PATH = Path("firmalar.jsonl")
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


@pytest.fixture()
def scraper(tmp_path):
    """Yazma hedefleri tmp_path'e bağlanmış DummyScraper döndürür."""
    scr = DummyScraper()
    scr.STATE_DIR = tmp_path
    scr.STATE_PATH = tmp_path / ".scrape_state.json"
    scr.OUTPUT_PATH = tmp_path / "firmalar.jsonl"
    return scr


def test_base_firma_to_jsonl():
    firma = DummyFirma(unvan="Test", web_sitesi="https://example.com")
    data = firma.to_jsonl()
    assert "Test" in data
    assert "example.com" in data


def test_normalize_website(scraper):
    assert scraper.normalize_website("example.com") == "https://example.com"
    assert scraper.normalize_website("https://example.com") == "https://example.com"
    assert scraper.normalize_website("blocked.com") is None
    assert scraper.normalize_website(None) is None
    assert scraper.normalize_website("") is None


def test_extract_vkn(scraper):
    assert scraper.extract_vkn("1234567890") == "1234567890"
    assert scraper.extract_vkn("firma 12345678901") == "12345678901"
    assert scraper.extract_vkn("no number") is None
    assert scraper.extract_vkn(None) is None


def test_state_management(scraper, tmp_path):
    state = scraper._load_state()
    assert "completed_pages" in state
    scraper._save_state({"completed_pages": [1], "total_records": 1})
    state2 = scraper._load_state()
    assert state2["completed_pages"] == [1]
    assert state2["total_records"] == 1
    # TEST-ISO-03: state dosyası tmp_path'te, gerçek repo dizinine yazmaz.
    assert scraper.STATE_PATH.parent == tmp_path
    assert (tmp_path / ".scrape_state.json").exists()


def test_scrape_yields_firmalar(scraper, tmp_path):
    gercek = Path("data/dummy/firmalar.jsonl")
    once = gercek.read_bytes() if gercek.exists() else None
    results = list(scraper.scrape(detay_al=False))
    assert len(results) == 1
    assert results[0].unvan == "Test Firma"
    # TEST-ISO-03: çıktı tmp_path'e yazıldı; gerçek data/dummy'ye dokunulmadı.
    assert (tmp_path / "firmalar.jsonl").exists()
    sonra = gercek.read_bytes() if gercek.exists() else None
    assert once == sonra, "TEST-ISO-03 ihlali: gerçek firmalar.jsonl testte değişti"
