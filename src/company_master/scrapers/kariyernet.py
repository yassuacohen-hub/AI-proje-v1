# -*- coding: utf-8 -*-
"""Kariyer.net scraper — hızlı MVP."""
from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup


@dataclass
class KariyerFirma:
    firma_adi: str
    sektor: str = ""
    konum: str = ""
    kaynak: str = "kariyer.net"
    cekilme_tarihi: str = field(default_factory=lambda: datetime.now().isoformat())


class KariyerNetScraper:
    BASE_URL = "https://www.kariyer.net"
    FIRMA_LISTE_URL = f"{BASE_URL}/firmalar/"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    RATE_LIMIT_SECONDS = 2.0
    OUTPUT_PATH = Path("data") / "kariyernet_firmalar.jsonl"
    log = logging.getLogger("kariyernet")

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

    def fetch(self, url: str, retries: int = 3, backoff: float = 2.0) -> str:
        for i in range(retries):
            try:
                resp = self.session.get(url, timeout=20)
                resp.raise_for_status()
                return resp.text
            except requests.RequestException:
                if i < retries - 1:
                    time.sleep(backoff * (i + 1))
                else:
                    raise
        return ""

    def parse(self, html: str) -> list[KariyerFirma]:
        soup = BeautifulSoup(html, "html.parser")
        firms: list[KariyerFirma] = []
        for card in soup.select("[class*='company'], [class*='firm'], .card"):
            ad_el = card.select_one("[class*='name'], h2, h3, .title")
            sektor_el = card.select_one("[class*='sector'], [class*='industry']")
            konum_el = card.select_one("[class*='location'], [class*='city']")
            firma_adi = ad_el.get_text(strip=True) if ad_el else ""
            if not firma_adi:
                continue
            firms.append(KariyerFirma(
                firma_adi=firma_adi,
                sektor=sektor_el.get_text(strip=True) if sektor_el else "",
                konum=konum_el.get_text(strip=True) if konum_el else "",
            ))
        return firms

    def save(self, firms: list[KariyerFirma]) -> None:
        seen: set[str] = set()
        self.OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with self.OUTPUT_PATH.open("a", encoding="utf-8") as f:
            for firma in firms:
                if firma.firma_adi in seen:
                    continue
                seen.add(firma.firma_adi)
                f.write(json.dumps(asdict(firma), ensure_ascii=False) + "\n")
