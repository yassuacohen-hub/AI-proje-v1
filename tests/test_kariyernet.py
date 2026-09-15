from __future__ import annotations
from unittest.mock import MagicMock, patch

import pytest

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
