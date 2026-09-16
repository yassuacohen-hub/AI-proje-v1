# -*- coding: utf-8 -*-
"""P7-28: Indeed İş İlanları Scraper.

Indeed public veri endpoint'leri ve HTML tabanli sayfalardan
is ilani verisi toplar. KVKK guvenli: sadece public ilanlar.

Akis:
  1. discover_job_urls() -> Indeed arama sonuclarindan URL'ler
  2. parse_job_detail() -> HTML'den ScrapedJob olusturur
  3. run_full_scrape() -> tam scrape
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from typing import Any
from urllib.parse import urljoin, urlparse, parse_qs

from bs4 import BeautifulSoup

from .base import BaseJobSource, ScrapedJob

logger = logging.getLogger(__name__)

INDEED_BASE = "https://www.indeed.com"
INDEED_SEARCH = "https://www.indeed.com/jobs"


class IndeedSource(BaseJobSource):
    """Indeed iş ilanları scraper."""

    def __init__(
        self,
        source_name: str = "indeed",
        domain: str = "www.indeed.com",
        min_interval: float = 3.0,
    ) -> None:
        super().__init__(
            source_name=source_name,
            domain=domain,
            min_interval=min_interval,
        )

    def discover_job_urls(
        self,
        query: str = "",
        location: str = "Turkey",
        max_pages: int = 10,
    ) -> list[str]:
        urls: list[str] = []
        for page in range(0, max_pages):
            start = page * 10
            params = f"?q={query}&l={location}&start={start}" if query else f"?l={location}&start={start}"
            urls.append(f"{INDEED_SEARCH}{params}")
        logger.info(
            "[%s] %d Indeed arama URL'si keşfedildi",
            self.source_name, len(urls),
        )
        return urls

    def parse_job_detail(self, html: str, url: str) -> ScrapedJob | None:
        soup = self._parse_html(html)

        structured = self._extract_json_ld(soup)
        if structured:
            return self._parse_from_structured(structured, url)

        return self._parse_from_html(soup, url)

    def _extract_json_ld(
        self, soup: BeautifulSoup
    ) -> dict[str, Any] | None:
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(self._safe_text(script.string or ""))
                if isinstance(data, list):
                    for item in data:
                        if item.get("@type") == "JobPosting":
                            return item
                elif data.get("@type") == "JobPosting":
                    return data
            except Exception:
                continue
        return None

    def _parse_from_structured(
        self, data: dict[str, Any], url: str
    ) -> ScrapedJob | None:
        try:
            title = data.get("title", "")
            description = data.get("description", "")
            company = data.get("hiringOrganization", {})
            company_name = company.get("name", "") if isinstance(company, dict) else ""
            location = data.get("jobLocation", {})
            if isinstance(location, dict):
                address = location.get("address", {})
                if isinstance(address, dict):
                    city = address.get("addressLocality", "")
                    country = address.get("addressCountry", "")
                else:
                    city = ""
                    country = ""
            else:
                city = ""
                country = ""

            return ScrapedJob(
                source_name=self.source_name,
                source_url=url,
                external_id=data.get("identifier", {}).get("value"),
                title=title,
                description=description,
                department="",
                seniority_level="",
                location_city=city,
                location_country=country or "Türkiye",
                employment_type=data.get("employmentType", ""),
                remote_type="remote" if "remote" in description.lower() else None,
                technologies=[],
                salary_min=None,
                salary_max=None,
                salary_currency="USD",
                posted_at=None,
                expired_at=None,
                raw_data=data,
            )
        except Exception as e:
            logger.debug("[%s] Indeed structured parse hata: %s", self.source_name, e)
            return None

    def _parse_from_html(
        self, soup: BeautifulSoup, url: str
    ) -> ScrapedJob | None:
        try:
            title_el = soup.find("h1", {"class": "jobsearch-JobTitle"})
            title = title_el.get_text(strip=True) if title_el else ""

            company_el = soup.find("span", {"class": "jobsearch-CompanyName"})
            company_name = company_el.get_text(strip=True) if company_el else ""

            description_el = soup.find("div", {"id": "jobDescriptionText"})
            description = description_el.get_text(strip=True) if description_el else ""

            location_el = soup.find("div", {"class": "jobsearch-JobMetadataFooter"})
            location = location_el.get_text(strip=True) if location_el else ""

            return ScrapedJob(
                source_name=self.source_name,
                source_url=url,
                external_id=None,
                title=title,
                description=description,
                department="",
                seniority_level="",
                location_city=location.split("—")[0].strip() if "—" in location else location,
                location_country="Türkiye",
                employment_type="",
                remote_type="remote" if "remote" in description.lower() else None,
                technologies=[],
                salary_min=None,
                salary_max=None,
                salary_currency="USD",
                posted_at=None,
                expired_at=None,
                raw_data={"url": url, "title": title, "company": company_name},
            )
        except Exception as e:
            logger.debug("[%s] Indeed HTML parse hata: %s", self.source_name, e)
            return None

    def run_full_scrape(
        self,
        query: str = "",
        location: str = "Turkey",
        max_pages: int = 10,
        output_file: str | None = None,
    ) -> list[ScrapedJob]:
        logger.info(
            "[%s] Indeed scrape baslıyor (query=%s, max_pages=%d)",
            self.source_name, query, max_pages,
        )

        urls = self.discover_job_urls(query=query, location=location, max_pages=max_pages)
        jobs: list[ScrapedJob] = []

        for url in urls:
            try:
                html = self._fetch(url)
                if html:
                    job = self.parse_job_detail(html, url)
                    if job:
                        jobs.append(job)
            except Exception as e:
                logger.debug("[%s] Indeed scrape hata (%s): %s", self.source_name, url, e)

        logger.info(
            "[%s] Indeed scrape tamamlandı: %d ilan",
            self.source_name, len(jobs),
        )

        if output_file and jobs:
            self._save_jsonl(jobs, output_file)

        return jobs
