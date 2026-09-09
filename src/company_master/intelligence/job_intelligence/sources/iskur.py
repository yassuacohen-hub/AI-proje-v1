# -*- coding: utf-8 -*-
"""Job Intelligence — İŞKUR Resmi İş İlanları Scraper (Basit Versiyon)."""
from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime
from typing import Any
from urllib.parse import urljoin, urlparse, parse_qs

from bs4 import BeautifulSoup

from .base import BaseJobSource, ScrapedJob, JOB_KEYWORDS

logger = logging.getLogger(__name__)

ISKUR_BASE = "https://www.iskur.gov.tr"
ISKUR_SEARCH = "https://www.iskur.gov.tr/is-ilanlari"


class IskurSource(BaseJobSource):
    """İŞKUR iş ilanları scraper (HTML tabanlı)."""
    
    def __init__(self):
        super().__init__(
            source_name="iskur",
            domain="www.iskur.gov.tr",
            min_interval=2.0
        )
    
    def discover_job_urls(self, max_pages: int = 10) -> list[str]:
        urls = [ISKUR_SEARCH]
        for page in range(2, max_pages + 1):
            urls.append(f"{ISKUR_SEARCH}?page={page}")
        return urls
    
    def parse_job_detail(self, html: str, url: str) -> ScrapedJob | None:
        soup = self._parse_html(html)
        
        # JSON-LD kontrol et
        structured = self._extract_json_ld(soup)
        if structured:
            return self._parse_from_structured(structured, url)
        
        return self._parse_from_html(soup, url)
    
    def _extract_json_ld(self, soup: BeautifulSoup) -> dict[str, Any] | None:
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
    
    def _parse_from_structured(self, data: dict[str, Any], url: str) -> ScrapedJob:
        hiring_org = data.get("hiringOrganization", {})
        company_name = hiring_org.get("name", "") if isinstance(hiring_org, dict) else ""
        
        location = data.get("jobLocation", {})
        city = ""
        if isinstance(location, dict):
            address = location.get("address", {})
            city = address.get("addressLocality", "") if isinstance(address, dict) else ""
        
        posted_at = None
        date_posted = data.get("datePosted")
        if date_posted:
            try:
                posted_at = datetime.fromisoformat(date_posted.replace("Z", "+00:00"))
            except Exception:
                pass
        
        salary_min = salary_max = None
        base_salary = data.get("baseSalary", {})
        if isinstance(base_salary, dict):
            value = base_salary.get("value", {})
            if isinstance(value, dict):
                salary_min = value.get("minValue")
                salary_max = value.get("maxValue")
        
        return ScrapedJob(
            source_name=self.source_name,
            source_url=url,
            external_id=data.get("identifier", {}).get("value") if data.get("identifier") else None,
            title=data.get("title", ""),
            description=data.get("description", ""),
            department=self._extract_department(data.get("description", "")),
            seniority_level=self._extract_seniority(data.get("description", "")),
            location_city=city,
            location_country="Türkiye",
            employment_type=data.get("employmentType", ""),
            remote_type=self._extract_remote_type(data.get("description", "")),
            technologies=self._extract_technologies(data.get("description", "")),
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency="TRY",
            posted_at=posted_at,
            expired_at=None,
            raw_data={"structured_data": True, "company_name": company_name, "url": url}
        )
    
    def _parse_from_html(self, soup: BeautifulSoup, url: str) -> ScrapedJob | None:
        title_elem = soup.select_one("h1, .ilan-baslik, .job-title, .title")
        title = self._safe_text(title_elem.get_text(strip=True)) if title_elem else ""
        
        if not title:
            return None
        
        desc_elem = soup.select_one(".ilan-aciklama, .job-description, .description, .content, .detail")
        description = self._safe_text(desc_elem.get_text(" ", strip=True)) if desc_elem else ""
        
        company_elem = soup.select_one(".firma-adi, .company-name, .employer, .sirket")
        company_name = self._safe_text(company_elem.get_text(strip=True)) if company_elem else ""
        
        loc_elem = soup.select_one(".lokasyon, .location, .sehir, .il, .ilce")
        city = self._safe_text(loc_elem.get_text(strip=True)) if loc_elem else ""
        
        date_elem = soup.select_one(".tarih, .date, .yayin-tarihi, .posted-date")
        posted_at = None
        if date_elem:
            posted_at = self._parse_turkish_date(self._safe_text(date_elem.get_text(strip=True)))
        
        salary_elem = soup.select_one(".maas, .salary, .ucret, .maas-araligi")
        salary_min, salary_max = self._parse_salary(self._safe_text(salary_elem.get_text(strip=True)) if salary_elem else "")
        
        type_elem = soup.select_one(".calisma-tipi, .employment-type, .calisma-sekli")
        employment_type = self._safe_text(type_elem.get_text(strip=True)) if type_elem else ""
        
        return ScrapedJob(
            source_name=self.source_name,
            source_url=url,
            external_id=self._extract_external_id(url),
            title=title,
            description=description,
            department=self._extract_department(description),
            seniority_level=self._extract_seniority(description),
            location_city=city,
            location_country="Türkiye",
            employment_type=employment_type or None,
            remote_type=self._extract_remote_type(description),
            technologies=self._extract_technologies(description),
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency="TRY",
            posted_at=posted_at,
            expired_at=None,
            raw_data={"company_name": company_name, "structured_data": False, "url": url}
        )
    
    def _parse_turkish_date(self, text: str) -> datetime | None:
        patterns = [
            r"(\d{1,2})\s+(\w+)\s+(\d{4})",
            r"(\d{2})\.(\d{2})\.(\d{4})",
            r"(\d{4})-(\d{2})-(\d{2})",
        ]
        months = {
            "ocak": 1, "şubat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "haziran": 6,
            "temmuz": 7, "ağustos": 8, "eylül": 9, "ekim": 10, "kasım": 11, "aralık": 12
        }
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    if pattern == patterns[0]:
                        day, month_str, year = match.groups()
                        month = months.get(month_str.lower())
                        if month:
                            return datetime(int(year), month, int(day))
                    elif pattern == patterns[1]:
                        day, month, year = match.groups()
                        return datetime(int(year), int(month), int(day))
                    elif pattern == patterns[2]:
                        year, month, day = match.groups()
                        return datetime(int(year), int(month), int(day))
                except Exception:
                    continue
        return None
    
    def _parse_salary(self, text: str) -> tuple[int | None, int | None]:
        if not text:
            return None, None
        numbers = re.findall(r"([\d\.]+)", text.replace(".", "").replace(",", ""))
        if not numbers:
            return None, None
        nums = [int(n) for n in numbers]
        if len(nums) >= 2:
            return min(nums), max(nums)
        elif len(nums) == 1:
            return nums[0], nums[0]
        return None, None
    
    def _extract_external_id(self, url: str) -> str | None:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        for key in ["id", "ilanId", "ilan_id", "jobId"]:
            if key in query:
                return query[key][0]
        return None
    
    def _extract_remote_type(self, text: str) -> str | None:
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["uzaktan", "remote", "evden", "home office", "hybrid", "hibrit"]):
            return "hybrid" if any(kw in text_lower for kw in ["hybrid", "hibrit"]) else "remote"
        return "onsite"
    
    def run_full_scrape(self, max_pages: int = 50, output_file: str | None = None) -> list[ScrapedJob]:
        logger.info("[%s] İŞKUR scrape başlıyor (max_pages=%d)", self.source_name, max_pages)
        
        urls = self.discover_job_urls(max_pages)
        all_jobs: list[ScrapedJob] = []
        
        for page_url in urls:
            html = self._fetch(page_url)
            if not html:
                continue
            
            soup = self._parse_html(html)
            job_links = self._extract_job_links(soup, page_url)
            
            for job_url in job_links:
                job_html = self._fetch(job_url)
                if not job_html:
                    continue
                
                job = self.parse_job_detail(job_html, job_url)
                if job:
                    all_jobs.append(job)
                
                time.sleep(0.3)
            
            if len(all_jobs) >= max_pages * 20:
                break
        
        logger.info("[%s] Scrape tamamlandı: %d ilan", self.source_name, len(all_jobs))
        
        if output_file and all_jobs:
            self._save_jsonl(all_jobs, output_file)
        
        return all_jobs
    
    def _extract_job_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        links = []
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if "/is-ilani/" in href or "/ilan/" in href or "/detay/" in href:
                full = urljoin(base_url, href)
                if urlparse(full).netloc == "www.iskur.gov.tr":
                    links.append(full)
        return list(set(links))
