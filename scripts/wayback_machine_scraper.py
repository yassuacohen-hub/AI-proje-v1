# -*- coding: utf-8 -*-
"""P7-29: Wayback Machine — Kariyer.net cache verisi toplama.

Kullanim:
    python scripts/wayback_machine_scraper.py --url "https://www.kariyer.net"
    python scripts/wayback_machine_scraper.py --url "https://www.kariyer.net" --timestamp 20260901000000
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

WAYBACK_API = "http://archive.org/wayback/available"
WAYBACK_BROWSER = "https://web.archive.org/web/{timestamp}/{url}"

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class WaybackScraper:
    """Wayback Machine'den Kariyer.net arsiv verisi toplar."""

    def __init__(self, max_results: int = 50, delay: float = 0.5) -> None:
        self.max_results = max_results
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        })
        self.results: list[dict[str, Any]] = []

    def check_availability(self, url: str) -> dict[str, Any] | None:
        """Wayback Machine'de URL icin snapshot kontrol et."""
        try:
            resp = self.session.get(
                WAYBACK_API,
                params={"url": url, "collapse": "urlkey"},
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("archived_snapshots"):
                    return data
            return None
        except requests.RequestException as e:
            logger.debug("Wayback API hata: %s", e)
            return None

    def fetch_snapshot(
        self,
        url: str,
        timestamp: str | None = None,
    ) -> str | None:
        """Wayback Machine'den snapshot getir."""
        if timestamp:
            target_url = WAYBACK_BROWSER.format(
                timestamp=timestamp, url=url
            )
        else:
            avail = self.check_availability(url)
            if not avail or not avail.get("archived_snapshots"):
                return None
            closest = avail["archived_snapshots"].get("closest")
            if not closest:
                return None
            ts = closest.get("timestamp", "")
            target_url = WAYBACK_BROWSER.format(timestamp=ts, url=url)

        try:
            resp = self.session.get(target_url, timeout=30)
            if resp.status_code == 200:
                return resp.text
            logger.debug("Snapshot sonucu: %d for %s", resp.status_code, url[:60])
        except requests.RequestException as e:
            logger.debug("Snapshot hata: %s for %s", e, url[:60])
        return None

    def discover_urls(
        self,
        domain: str = "kariyer.net",
        path_prefix: str = "",
    ) -> list[str]:
        """CDX API ile bucket/dizin keşfeti."""
        cdx_url = "http://web.archive.org/cdx/search/cdx"
        urls: list[str] = []
        url_pattern = f"https://{domain}/{path_prefix}*"

        params = {
            "url": url_pattern,
            "output": "json",
            "limit": self.max_results,
            "fl": "original",
            "filter": "mimetype:text/html",
            "statuscode": "200",
        }

        try:
            resp = self.session.get(cdx_url, params=params, timeout=30)
            if resp.status_code == 200:
                lines = resp.text.strip().split("\n")
                for line in lines[1:]:
                    url = line.strip()
                    if url and domain in url:
                        urls.append(url)
            logger.info("CDX'ten %d URL bulundu", len(urls))
        except requests.RequestException as e:
            logger.warning("CDX hata: %s", e)

        return urls

    def scrape(
        self,
        domain: str = "kariyer.net",
        paths: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Belirtilen yollari Wayback'ten scrape et."""
        if paths is None:
            paths = [
                "/is-ilanlari",
                "/kariyer-net",
                "/is-bulun",
            ]

        for path in paths:
            url = f"https://{domain}{path}"
            logger.info("Wayback scrape: %s", url)

            snap = self.fetch_snapshot(url)
            if snap:
                self.results.append({
                    "url": url,
                    "timestamp": snap[:19] if snap else "",
                    "source": "wayback",
                    "html_length": len(snap),
                    "fetched": True,
                })
            time.sleep(self.delay)

        return self.results

    def save_results(
        self,
        output_file: str = "data/job_intelligence/wayback_kariyer_results.jsonl",
    ) -> None:
        """Sonuclari JSONL olarak kaydet."""
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for r in self.results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        logger.info("Wayback sonuclari kaydedildi: %s (%d kayit)", path, len(self.results))


def main() -> None:
    parser = argparse.ArgumentParser(description="Wayback Machine: Kariyer.net cache")
    parser.add_argument("--url", default="https://www.kariyer.net", help="Ana URL")
    parser.add_argument("--timestamp", default=None, help="Snapshot zaman damgasi")
    parser.add_argument("--paths", nargs="*", default=["/is-ilanlari", "/kariyer-net"], help="Yollar")
    parser.add_argument("--output", default="data/job_intelligence/wayback_kariyer_results.jsonl", help="Cikti")
    args = parser.parse_args()

    scraper = WaybackScraper(max_results=50)

    parsed = urlparse(args.url)
    domain = parsed.netloc

    urls = scraper.discover_urls(domain=domain)
    print(f"CDX'ten {len(urls)} URL bulundu")

    scraper.scrape(domain=domain, paths=args.paths)
    scraper.save_results(args.output)

    print(f"Sonuc: {len(scraper.results)} kayit -> {args.output}")


if __name__ == "__main__":
    main()
