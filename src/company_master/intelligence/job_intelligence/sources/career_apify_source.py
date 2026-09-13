# -*- coding: utf-8 -*-
"""P7-4: Career Pages Apify Source — Apify actor ile kariyer sayfası scraper.

Mevcut CompanyCareerSource (HTML tabanli) ile ayni işi yapar
ama Apify cloud actor uzerinden. Rate limit ve auth Apify tarafindan
yönetilir. KVKK guvenli: sadece firma kendi sitesindeki veriyi toplar.

Akis:
  1. ApifyJobSource.start_actor() -> Actor run baslatir
  2. Dataset sayfalari okunur (limit/offset)
  3. ScrapedJob formatina donusulur
  4. Rate limit Apify API tarafindan yonetilir
"""
from __future__ import annotations

import logging
from typing import Any

from company_master.intelligence.job_intelligence.sources.apify_job_source import (
    ApifyJobSource,
)
from company_master.intelligence.job_intelligence.sources.base import (
    ScrapedJob,
)

logger = logging.getLogger(__name__)

CAREER_ACTOR_INPUT = {
    "startUrls": [],
    "maxPages": 50,
    "maxCrawledPages": 200,
}


class CareerPagesApifySource(ApifyJobSource):
    """Apify Actor uzerinden şirket kariyer sayfalarindan ilan toplar.

    Args:
        actor_id: Apify Actor kimligi (default: apify/website-crawler)
        apify_token: Apify API token (varsayilan: APIFY_TOKEN env)
        max_pages: Maksimum kare page sayisi
        min_interval: Min istek araligi (Apify'de kullilmaz, log icin)
    """

    def __init__(
        self,
        source_name: str = "career-pages-apify",
        actor_id: str = "apify/website-crawler",
        apify_token: str | None = None,
        max_pages: int = 50,
    ) -> None:
        super().__init__(
            source_name=source_name,
            actor_id=actor_id,
            domain=None,
            min_interval=2.0,
            apify_token=apify_token,
        )
        self.max_pages = max_pages
        self._company_urls: list[str] = []

    def set_company_urls(self, urls: list[str]) -> None:
        """Kariyer sayfalari URL'lerini ayarlar."""
        self._company_urls = urls

    def _build_run_input(self) -> dict[str, Any]:
        """Actor calistirma icin input olusturur."""
        urls = self._company_urls[: self.max_pages]
        return {
            **CAREER_ACTOR_INPUT,
            "startUrls": urls,
            "maxPages": min(self.max_pages, len(urls)) if urls else 1,
        }

    def discover_job_urls(self, max_pages: int | None = None) -> list[str]:
        """Apify actor ile kariyer sayfası URL'lerini keşfetir."""
        run_input = self._build_run_input()
        logger.info(
            "[%s] Apify actor calistiriliyor: actor=%s, %d URL",
            self.source_name, self.actor_id, len(run_input["startUrls"]),
        )
        self._start_actor(run_input)
        items = self._fetch_dataset(limit=self.max_pages * 10)
        urls = [
            item.get("url", item.get("link", ""))
            for item in items
            if item.get("url") or item.get("link")
        ]
        logger.info(
            "[%s] Toplam %d kariyer sayfası URL'de bulundu",
            self.source_name, len(urls),
        )
        return urls

    def parse_job_detail(self, html: str, url: str) -> ScrapedJob | None:
        """Tek ilan detayini parse eder."""
        jobs = self.parse_job_listing(html, url)
        return jobs[0] if jobs else None

    def parse_job_listing(
        self, html: str, url: str
    ) -> list[ScrapedJob]:
        """HTML'den ScrapedJob listesi uretir."""
        from bs4 import BeautifulSoup
        from company_master.intelligence.job_intelligence.sources.base import (
            JOB_KEYWORDS,
        )

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True).lower()

        if not any(kw in text for kw in JOB_KEYWORDS):
            return []

        job_cards: list[ScrapedJob] = []
        for selector in [
            "div[class*='job']", "li[class*='job']", "article[class*='job']",
            "div[class*='career']", "div[class*='position']",
            "div[class*='listing']", ".job-list li", ".career-list li",
        ]:
            elements = soup.select(selector)
            if elements:
                job_cards = elements
                break

        if not job_cards:
            for link in soup.find_all("a", href=True):
                link_text = link.get_text(" ", strip=True).lower()
                if any(kw in link_text for kw in JOB_KEYWORDS):
                    job_cards.append(link)

        if not job_cards:
            return []

        site_domain = url.split("/")[2] if "://" in url else "unknown"
        scraped: list[ScrapedJob] = []
        for idx, card in enumerate(job_cards[:50]):
            card_text = card.get_text(" ", strip=True)
            href = card.get("href", "")
            scraped.append(ScrapedJob(
                source_name=self.source_name,
                source_url=f"{url}#{idx}",
                external_id=f"apify-career:{site_domain}:{idx}",
                title=card_text[:200] or f"Career Page {idx+1}",
                description=card_text[:500],
                department=None,
                seniority_level=None,
                location_city=None,
                location_country="Türkiye",
                employment_type=None,
                remote_type=None,
                technologies=None,
                salary_min=None,
                salary_max=None,
                salary_currency="TRY",
                posted_at=None,
                expired_at=None,
                raw_data={
                    "career_page_url": url,
                    "job_cards_found": len(job_cards),
                    "company_domain": site_domain,
                    "actor_id": self.actor_id,
                },
            ))
        return scraped
