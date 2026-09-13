# -*- coding: utf-8 -*-
"""P7-28: LinkedIn İş İlanları Apify Source.

LinkedIn anti-bot koruması nedeniyle Apify actor uzerinden
celistirilir. KVKK guvenli: sadece public is ilani verisi toplanir.

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

LINKEDIN_ACTOR_ID = "apify/linkedin-company-jobs"

LINKEDIN_ACTOR_INPUT = {
    "query": "",
    "type": "company",
    "locationName": "Turkey",
    "startPage": 0,
    "maxPages": 20,
}


class LinkedInApifySource(ApifyJobSource):
    """Apify Actor uzerinden LinkedIn is ilanlarini toplar.

    Args:
        actor_id: Apify Actor kimligi (default: apify/linkedin-company-jobs)
        apify_token: Apify API token (varsayilan: APIFY_TOKEN env)
        max_pages: Maksimum sayfa sayisi
        company_name: Sirket adi ile filtrele (opsiyonel)
        location: Konum filtresi (default: Turkey)
    """

    def __init__(
        self,
        source_name: str = "linkedin-jobs",
        actor_id: str = LINKEDIN_ACTOR_ID,
        apify_token: str | None = None,
        max_pages: int = 20,
        company_name: str | None = None,
        location: str = "Turkey",
    ) -> None:
        super().__init__(
            source_name=source_name,
            actor_id=actor_id,
            domain="www.linkedin.com",
            min_interval=5.0,
            apify_token=apify_token,
        )
        self.max_pages = max_pages
        self.company_name = company_name
        self.location = location

    def _build_run_input(self) -> dict[str, Any]:
        run_input = {
            "query": self.company_name or "",
            "type": "company",
            "locationName": self.location,
            "startPage": 0,
            "maxPages": self.max_pages,
        }
        return run_input

    def discover_job_urls(self, max_pages: int | None = None) -> list[str]:
        effective_max = max_pages or self.max_pages
        run_input = self._build_run_input()
        run_input["maxPages"] = effective_max

        run_id = self._start_actor(run_input)
        items = self._fetch_dataset(limit=effective_max * 10)

        urls = [item.get("url", item.get("link", "")) for item in items if item.get("url") or item.get("link")]
        logger.info(
            "[%s] %d LinkedIn URL'si keşfedildi (run_id=%s)",
            self.source_name, len(urls), run_id,
        )
        return urls

    def parse_job_detail(self, html: str, url: str) -> ScrapedJob | None:
        return None

    def run_full_scrape(
        self, max_pages: int | None = None, output_file: str | None = None
    ) -> list[ScrapedJob]:
        effective_max = max_pages or self.max_pages
        logger.info(
            "[%s] LinkedIn scrape baslıyor (max_pages=%d)",
            self.source_name, effective_max,
        )

        run_input = self._build_run_input()
        run_input["maxPages"] = effective_max

        run_id = self._start_actor(run_input)
        items = self._fetch_dataset(limit=effective_max * 10)

        jobs: list[ScrapedJob] = []
        for item in items:
            job = self._apify_item_to_scraped_job(item)
            if job:
                jobs.append(job)

        logger.info(
            "[%s] LinkedIn scrape tamamlandı: %d ilan",
            self.source_name, len(jobs),
        )

        if output_file and jobs:
            self._save_jsonl(jobs, output_file)

        return jobs
