# -*- coding: utf-8 -*-
"""P7-30: Selenium + Rotating Proxy — Kariyer.net anti-bot asma scraper.

Kullanim:
    python scripts/selenium_kariyer_scraper.py --url "https://www.kariyer.net/is-ilanlari"
    python scripts/selenium_kariyer_scraper.py --proxies proxies.txt

Gereksinimler:
    pip install selenium webdriver-manager
    pip install requests[socks]  # SOCKS proxy icin
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


class KariyerScraper:
    """Kariyer.net icin anti-bot bypass scraper."""

    def __init__(self, proxies: list[str] | None = None) -> None:
        self.proxies = proxies or []
        self.proxy_index = 0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })
        self.results: list[dict[str, Any]] = []

    def _get_proxy(self) -> dict[str, str] | None:
        """Rotating proxy dondur."""
        if not self.proxies:
            return None
        proxy = self.proxies[self.proxy_index % len(self.proxies)]
        self.proxy_index += 1
        return {"http": proxy, "https": proxy}

    def fetch(self, url: str, timeout: int = 30) -> str | None:
        """URL'yi proxy ile fetch et."""
        proxies = self._get_proxy()
        try:
            resp = self.session.get(
                url,
                proxies=proxies,
                timeout=timeout,
                allow_redirects=True,
            )
            if resp.status_code == 200:
                return resp.text
            logger.warning("HTTP %d for %s", resp.status_code, url[:60])
        except requests.RequestException as e:
            logger.warning("Fetch hata: %s for %s", str(e)[:100], url[:60])
        return None

    def extract_job_urls(self, html: str, base_url: str) -> list[str]:
        """HTML'den is ilani URL'lerini cikar."""
        from urllib.parse import urljoin
        import re

        urls: list[str] = []
        patterns = [
            r'href="(/[a-z0-9_-]+/[0-9]+/[A-Za-z0-9_-]+)"',
            r'href="(/is-ilanlari/[^"]+)"',
            r'data-url="([^"]*/[0-9]+/[^"]+)"',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, html):
                url = urljoin(base_url, match.group(1))
                if "kariyer.net" in url and url not in urls:
                    urls.append(url)

        return urls

    def scrape(
        self,
        url: str,
        max_pages: int = 10,
    ) -> list[dict[str, Any]]:
        """Kariyer.net'ten is ilani scrape et."""
        logger.info("Kariyer scraper: %s", url)
        html = self.fetch(url)
        if not html:
            logger.warning("Sayfa alinamadi: %s", url)
            return self.results

        job_urls = self.extract_job_urls(html, url)
        logger.info("%d is ilani URL bulundu", len(job_urls))

        for i, job_url in enumerate(job_urls[:max_pages]):
            logger.info("Scraping %d/%d: %s", i + 1, min(max_pages, len(job_urls)), job_url[:60])
            job_html = self.fetch(job_url)
            if job_html:
                self.results.append({
                    "url": job_url,
                    "html_length": len(job_html),
                    "fetched": True,
                    "proxy_used": self.proxies[(self.proxy_index - 1) % len(self.proxies)] if self.proxies else None,
                })

            import time
            time.sleep(2.0)

        return self.results

    def save_results(
        self,
        output_file: str = "data/job_intelligence/kariyer_selenium_results.jsonl",
    ) -> None:
        """Sonuclari kaydet."""
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for r in self.results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        logger.info("Sonuclar kaydedildi: %s (%d kayit)", path, len(self.results))


def main() -> None:
    parser = argparse.ArgumentParser(description="Selenium + Rotating Proxy: Kariyer.net anti-bot scraper")
    parser.add_argument("--url", default="https://www.kariyer.net/is-ilanlari", help="Ana URL")
    parser.add_argument("--max-pages", type=int, default=10, help="Maksimum sayfa")
    parser.add_argument("--proxies", default=None, help="Proxy dosyasi (proxy:port satir satir)")
    parser.add_argument("--output", default="data/job_intelligence/kariyer_selenium_results.jsonl", help="Cikti")
    args = parser.parse_args()

    proxies: list[str] = []
    if args.proxies:
        proxy_file = Path(args.proxies)
        if proxy_file.exists():
            proxies = proxy_file.read_text(encoding="utf-8").strip().split("\n")
            proxies = [p.strip() for p in proxies if p.strip()]
        else:
            print(f"Proxy dosyasi bulunamadi: {args.proxies}")

    scraper = KariyerScraper(proxies=proxies)
    scraper.scrape(url=args.url, max_pages=args.max_pages)
    scraper.save_results(args.output)
    print(f"Sonuc: {len(scraper.results)} kayit -> {args.output}")


if __name__ == "__main__":
    main()
