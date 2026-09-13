# -*- coding: utf-8 -*-
"""P7-30: Kariyer.net Selenium Source — Anti-bot bypass source.

Selenium + rotating proxy ile Kariyer.net'den is ilani scrape eder.
Proxy rotator ve user-agent rotation destekler.

Kullanim:
    from src.company_master.intelligence.job_intelligence.sources.kariyer_selenium_source import KariyerSeleniumSource
    source = KariyerSeleniumSource()
    jobs = source.run_full_scrape(max_pages=10)
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from company_master.intelligence.job_intelligence.sources.base import BaseJobSource, ScrapedJob
from company_master.utils.proxy_rotator import ProxyRotator

logger = logging.getLogger(__name__)

KARIYER_BASE = "https://www.kariyer.net"
KARIYER_SEARCH = "https://www.kariyer.net/is-ilanlari"


class KariyerSeleniumSource(BaseJobSource):
    """Selenium + rotating proxy ile Kariyer.net is ilani scraper.

    Not: Selenium ve webdriver-manager gereklidir.
    pip install selenium webdriver-manager
    """

    def __init__(
        self,
        source_name: str = "kariyer-selenium",
        domain: str = "www.kariyer.net",
        min_interval: float = 3.0,
        max_pages: int = 10,
    ) -> None:
        super().__init__(
            source_name=source_name,
            domain=domain,
            min_interval=min_interval,
        )
        self.max_pages = max_pages
        self.proxy_rotator = ProxyRotator()
        self._driver: Any = None

    def _init_driver(self) -> None:
        """Selenium driver olustur (gerekirse)."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager

            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            user_agent = self.proxy_rotator.get_user_agent()
            options.add_argument(f"--user-agent={user_agent}")

            if self.proxy_rotator.current_proxy:
                proxy = self.proxy_rotator.current_proxy
                options.add_argument(f"--proxy-server={proxy}")

            service = Service(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service, options=options)
            logger.info("Selenium driver olusturuldu")
        except Exception as e:
            logger.warning("Selenium driver olusturulamadi: %s", e)
            self._driver = None

    def discover_job_urls(self, max_pages: int | None = None) -> list[str]:
        """Sayfalardan URL cikar."""
        effective_max = max_pages or self.max_pages
        urls: list[str] = []

        if self._driver is None:
            self._init_driver()

        if self._driver:
            try:
                for page in range(1, effective_max + 1):
                    url = f"{KARIYER_SEARCH}?p={page}"
                    self._driver.get(url)
                    time.sleep(self.min_interval)

                    from selenium.webdriver.common.by import By
                    links = self._driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute("href")
                        if href and "kariyer.net" in href and "/is-ilan/" in href:
                            if href not in urls:
                                urls.append(href)

                    if len(urls) >= effective_max * 5:
                        break
            except Exception as e:
                logger.warning("Selenium scrape hata: %s", e)
        else:
            logger.info("Selenium driver yok — HTTP ile dene")
            import requests
            for page in range(1, effective_max + 1):
                url = f"{KARIYER_SEARCH}?p={page}"
                proxy = self.proxy_rotator.get_proxy()
                try:
                    resp = requests.get(url, proxies=proxy, timeout=30)
                    if resp.status_code == 200:
                        import re
                        from urllib.parse import urljoin
                        for m in re.finditer(r'href="(/is-ilan/[^"]+)"', resp.text):
                            full = urljoin(KARIYER_BASE, m.group(1))
                            if full not in urls:
                                urls.append(full)
                except Exception:
                    continue

        logger.info("%d Kariyer.net URL bulundu", len(urls))
        return urls[: effective_max * 5]

    def parse_job_detail(self, html: str, url: str) -> ScrapedJob | None:
        """HTML'den ScrapedJob olustur."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        try:
            title_el = soup.find("h1")
            title = title_el.get_text(strip=True) if title_el else ""

            desc_el = soup.find("div", {"class": "job-detail"}) or soup.find("div", id="jobDescriptionText")
            description = desc_el.get_text(strip=True) if desc_el else ""

            return ScrapedJob(
                source_name=self.source_name,
                source_url=url,
                external_id=None,
                title=title,
                description=description,
                department="",
                seniority_level="",
                location_city="",
                location_country="Turkiye",
                employment_type="",
                remote_type=None,
                technologies=[],
                salary_min=None,
                salary_max=None,
                salary_currency="TRY",
                posted_at=None,
                expired_at=None,
                raw_data={"url": url, "title": title},
            )
        except Exception as e:
            logger.debug("Kariyer parse hata: %s", e)
            return None

    def run_full_scrape(
        self,
        max_pages: int | None = None,
        output_file: str | None = None,
    ) -> list[ScrapedJob]:
        """Tam scrape."""
        logger.info("[%s] Kariyer scrape baslıyor", self.source_name)
        urls = self.discover_job_urls(max_pages=max_pages)
        jobs: list[ScrapedJob] = []

        for url in urls:
            try:
                proxy = self.proxy_rotator.get_proxy()
                headers = {"User-Agent": self.proxy_rotator.get_user_agent()}
                import requests
                resp = requests.get(url, proxies=proxy, headers=headers, timeout=30)
                if resp.status_code == 200:
                    job = self.parse_job_detail(resp.text, url)
                    if job:
                        jobs.append(job)
            except Exception as e:
                logger.debug("Scrape hata: %s", e)

            if len(jobs) % 10 == 0:
                logger.info("Islem: %d/%d", len(jobs), len(urls))

        logger.info("[%s] Kariyer scrape tamamlandi: %d ilan", self.source_name, len(jobs))

        if output_file and jobs:
            self._save_jsonl(jobs, output_file)

        return jobs

    def _save_jsonl(self, jobs: list[ScrapedJob], output_file: str) -> None:
        """JSONL olarak kaydet."""
        import json
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for job in jobs:
                d = job.model_dump() if hasattr(job, "model_dump") else job.__dict__
                f.write(json.dumps(d, ensure_ascii=False, default=str) + "\n")
        logger.info("Kaydedildi: %s (%d ilan)", path, len(jobs))
