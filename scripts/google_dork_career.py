# -*- coding: utf-8 -*-
"""P7-29: Google Dorking — Kariyer.net cache verisi toplama.

Kullanim:
    python scripts/google_dork_career.py --query "site:kariyer.net" --max 50
    python scripts/google_dork_career.py --query "software engineer" --location "Istanbul" --max 20
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import time
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

GOOGLE_SEARCH_URL = "https://www.google.com/search"
GOOGLE_CACHE_URL = "https://webcache.googleusercontent.com/search"

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


class GoogleDorker:
    """Google Dork sorgulari ile Kariyer.net verisi toplar."""

    def __init__(self, max_results: int = 50, delay: float = 1.0) -> None:
        self.max_results = max_results
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        })
        self.results: list[dict[str, Any]] = []

    def search(self, query: str) -> list[dict[str, Any]]:
        """Google dork sorgusu yap ve sonuclari topla."""
        logger.info("Google dork sorgusu: %s", query)
        start = 0
        per_page = 10

        while len(self.results) < self.max_results:
            params: dict[str, Any] = {
                "q": query,
                "num": per_page,
                "start": start,
                "hl": "tr",
                "gl": "tr",
            }
            try:
                resp = self.session.get(GOOGLE_SEARCH_URL, params=params, timeout=30)
                if resp.status_code != 200:
                    logger.warning("Google arama sonucu: %d", resp.status_code)
                    break

                links = self._extract_links(resp.text)
                if not links:
                    break

                for link in links:
                    if "kariyer.net" in link and not any(r.get("url") == link for r in self.results):
                        self.results.append({
                            "url": link,
                            "source": "google",
                            "query": query,
                            "fetched": False,
                        })

                if len(links) < per_page:
                    break

                start += per_page
                time.sleep(self.delay)

            except requests.RequestException as e:
                logger.warning("Google arama hata: %s", e)
                break

        logger.info("Toplam %d Kariyer.net sonucu bulundu", len(self.results))
        return self.results

    def _extract_links(self, html: str) -> list[str]:
        """HTML'den baglanti cikar."""
        pattern = r'<a\s+href="(/url\?q=)([^"]+)"'
        matches = re.findall(pattern, html)
        urls = []
        for _, url in matches:
            try:
                from urllib.parse import unquote
                decoded = unquote(url)
                if "kariyer.net" in decoded and "&amp;" not in decoded[:50]:
                    urls.append(decoded.split("&amp;")[0])
            except Exception:
                continue
        return urls

    def fetch_cache(self, url: str) -> str | None:
        """Google cache'den sayfa icerigini getir."""
        params = {"q": url}
        try:
            resp = self.session.get(GOOGLE_CACHE_URL, params=params, timeout=30)
            if resp.status_code == 200:
                return resp.text
            logger.debug("Cache sonucu: %d for %s", resp.status_code, url[:60])
        except requests.RequestException as e:
            logger.debug("Cache hata: %s for %s", e, url[:60])
        return None

    def save_results(self, output_file: str = "data/job_intelligence/kariyer_dork_results.jsonl") -> None:
        """Sonuclari JSONL olarak kaydet."""
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for r in self.results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        logger.info("Sonuclar kaydedildi: %s (%d kayit)", path, len(self.results))


def main() -> None:
    parser = argparse.ArgumentParser(description="Google Dorking: Kariyer.net cache verisi")
    parser.add_argument("--query", default="site:kariyer.net", help="Google dork sorgusu")
    parser.add_argument("--max", type=int, default=50, help="Maksimum sonuc sayisi")
    parser.add_argument("--output", default="data/job_intelligence/kariyer_dork_results.jsonl", help="Cikti dosyasi")
    parser.add_argument("--fetch-cache", action="store_true", help="Google cache'den fetch et")
    args = parser.parse_args()

    dorker = GoogleDorker(max_results=args.max)
    dorker.search(args.query)

    if args.fetch_cache and dorker.results:
        for r in dorker.results[:10]:
            html = dorker.fetch_cache(r["url"])
            if html:
                r["cache_html"] = html[:5000]
                r["fetched"] = True
            time.sleep(1.0)

    dorker.save_results(args.output)
    print(f"Sonuc: {len(dorker.results)} kayit -> {args.output}")


if __name__ == "__main__":
    main()
