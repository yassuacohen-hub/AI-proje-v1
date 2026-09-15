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
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


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
    OUTPUT_PATH = Path(__file__).resolve().parents[3] / "data" / "kariyernet_firmalar.jsonl"
    log = logging.getLogger("kariyernet")

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

    def _robots_izinli(self, url: str) -> bool:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = RobotFileParser(robots_url)
        try:
            rp.read()
            return rp.can_fetch(self.USER_AGENT, url)
        except Exception:
            return True

    def fetch(self, url: str, retries: int = 3, backoff: float = 2.0) -> str:
        if not self._robots_izinli(url):
            raise PermissionError(f"robots.txt ile erişim engellendi: {url}")
        for i in range(retries):
            try:
                resp = self.session.get(url, timeout=20)
                resp.raise_for_status()
                return resp.text
            except requests.RequestException:
                if i < retries - 1:
                    time.sleep(self.RATE_LIMIT_SECONDS)
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
        if self.OUTPUT_PATH.exists():
            for line in self.OUTPUT_PATH.read_text(encoding="utf-8").splitlines():
                try:
                    entry = json.loads(line)
                    seen.add(entry.get("firma_adi", ""))
                except json.JSONDecodeError:
                    continue
        with self.OUTPUT_PATH.open("a", encoding="utf-8") as f:
            for firma in firms:
                if firma.firma_adi in seen:
                    continue
                seen.add(firma.firma_adi)
                f.write(json.dumps(asdict(firma), ensure_ascii=False) + "\n")
