from __future__ import annotations
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.company_master.scrapers.kariyernet import KariyerNetScraper, KariyerFirma


HTML = """
<div>
  <div class="company-card">
    <h3>Acme Inc</h3>
    <span class="sector">Teknoloji</span>
    <span class="location">Ankara</span>
  </div>
  <div class="firm-card">
    <h2>Beta Ltd</h2>
    <span class="industry">İmalat</span>
    <span class="city">İstanbul</span>
  </div>
</div>
"""


def test_fetch_success():
    scraper = KariyerNetScraper()
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.text = "<html></html>"
    fake_resp.raise_for_status = MagicMock()
    with patch.object(scraper.session, "get", return_value=fake_resp):
        result = scraper.fetch("https://www.kariyer.net/firmalar/")
    assert result == "<html></html>"


def test_parse_extracts_company_data():
    scraper = KariyerNetScraper()
    firms = scraper.parse(HTML)
    assert len(firms) == 2
    assert firms[0].firma_adi == "Acme Inc"
    assert firms[0].sektor == "Teknoloji"
    assert firms[0].konum == "Ankara"
    assert firms[1].firma_adi == "Beta Ltd"


def test_output_path_repo_kokune_bagli():
    expected = Path(__file__).resolve().parents[1] / "data" / "kariyernet_firmalar.jsonl"
    assert KariyerNetScraper.OUTPUT_PATH == expected


def test_fetch_rate_limit_sleep(monkeypatch):
    sleeps = []
    monkeypatch.setattr("time.sleep", lambda s: sleeps.append(s))
    scraper = KariyerNetScraper()
    fail_resp = MagicMock()
    fail_resp.raise_for_status.side_effect = requests.RequestException("boom")
    ok_resp = MagicMock()
    ok_resp.status_code = 200
    ok_resp.text = "<html></html>"
    ok_resp.raise_for_status = MagicMock()
    with patch.object(scraper.session, "get", side_effect=[fail_resp, fail_resp, ok_resp]):
        result = scraper.fetch("https://www.kariyer.net/firmalar/", retries=3)
    assert result == "<html></html>"
    assert len(sleeps) == 2
    assert all(s == 2.0 for s in sleeps)


def test_save_kalici_dedup(tmp_path, monkeypatch):
    output = tmp_path / "firmalar.jsonl"
    monkeypatch.setattr(KariyerNetScraper, "OUTPUT_PATH", output)
    KariyerNetScraper.save(KariyerNetScraper(), [KariyerFirma(firma_adi="Acme", sektor="Tech", konum="Ankara")])
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    KariyerNetScraper.save(KariyerNetScraper(), [KariyerFirma(firma_adi="Acme", sektor="Tech2", konum="Izmir")])
    lines = output.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1


def test_fetch_robots_engelleme(monkeypatch):
    scraper = KariyerNetScraper()
    monkeypatch.setattr(scraper, "_robots_izinli", lambda url: False)
    with pytest.raises(PermissionError, match="robots.txt"):
        scraper.fetch("https://www.kariyer.net/firmalar/")
