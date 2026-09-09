#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""İş ilanları ve çalışan sayısı çıkarıcı - şirket web sitelerinden."""
from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from sqlalchemy import text
from company_master.db.connection import get_engine

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "job_postings_scraper.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("job_postings_scraper")

CAREER_PATHS = ["/kariyer", "/is-ilanlari", "/isbasvuru", "/basvuru", "/calisma-hayati", "/insan-kaynaklari", "/career", "/careers", "/jobs"]
ABOUT_PATHS = ["/hakkimizda", "/hakkinda", "/about", "/about-us", "/kurumsal", "/firmamiz"]

EMPLOYEE_PATTERNS = [
    r'(\d{1,4})\s*(?:çalışan|personel|kadro|employee|staff)',
    r'(?:çalışan|personel|kadro|employee|staff)\s*(?:sayısı|adedi)?\s*[:\-]?\s*(\d{1,4})',
    r'(\d{1,4})\s*kisi',
    r'ekip\s*(?:büyüklüğü|sayısı)?\s*[:\-]?\s*(\d{1,4})',
    r'team\s*(?:size)?\s*[:\-]?\s*(\d{1,4})',
]

JOB_KEYWORDS = [
    "iş ilan", "açık pozisyon", "kariyer fırsat", "job opening", "vacancy",
    "positions", "kariera", "iş fırsatı", "yeni takım", "join us", "join our team",
    "başvuru", "apply now", "işe alım", "pozisyonlar", "acik pozisyon",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def fetch_page(url: str, timeout: int = 10) -> str | None:
    try:
        resp = SESSION.get(url, timeout=timeout, verify=False, allow_redirects=True)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or 'utf-8'
        return resp.text
    except requests.RequestException as e:
        log.debug("Fetch failed for %s: %s", url, e)
        return None


def safe_text(text: str) -> str:
    if not text:
        return ""
    try:
        return text.encode('utf-8', errors='ignore').decode('utf-8')
    except Exception:
        return text
def extract_job_count(html: str, base_url: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    text = safe_text(soup.get_text(" ", strip=True)).lower()
    
    for kw in JOB_KEYWORDS:
        idx = text.find(kw.lower())
        if idx >= 0:
            context = text[max(0, idx-150):idx+150]
            numbers = re.findall(r'\b(\d{1,3})\b', context)
            for n in numbers:
                val = int(n)
                if 1 <= val <= 200:
                    log.debug("Job count from keyword '%s': %d", kw, val)
                    return val
    
    job_selectors = [
        "div[class*='job']", "li[class*='job']", "article[class*='job']",
        "div[class*='career']", "li[class*='career']",
        "div[class*='position']", "li[class*='position']",
        "div[class*='ilan']", "li[class*='ilan']",
        "div[class*='pozisyon']", "li[class*='pozisyon']",
        ".job-list li", ".career-list li", ".positions li",
    ]
    max_count = 0
    for selector in job_selectors:
        try:
            elements = soup.select(selector)
            if len(elements) > max_count:
                max_count = len(elements)
        except Exception:
            pass
    
    if max_count > 1:
        log.debug("Job count from cards: %d", max_count)
        return min(max_count, 200)
    
    try:
        pagination = soup.select("nav[class*='pag'] a, .pagination a, .pager a")
        page_nums = [int(p.get_text(strip=True)) for p in pagination if p.get_text(strip=True).isdigit()]
        if page_nums:
            return max(page_nums) * 10
    except Exception:
        pass
    
    return 0


def extract_employee_count(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    text = safe_text(soup.get_text(" ", strip=True))
    
    for pattern in EMPLOYEE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                for m in match:
                    if m.isdigit():
                        val = int(m)
                        if 1 <= val <= 10000:
                            log.debug("Employee count from pattern: %d", val)
                            return val
            elif match.isdigit():
                val = int(match)
                if 1 <= val <= 10000:
                    log.debug("Employee count from pattern: %d", val)
                    return val
    
    try:
        for script in soup.find_all("script", type="application/ld+json"):
            data = json.loads(safe_text(script.string or ""))
            if isinstance(data, dict) and data.get("@type") == "Organization":
                emp = data.get("numberOfEmployees")
                if emp:
                    if isinstance(emp, dict) and "value" in emp:
                        return int(emp["value"])
                    elif isinstance(emp, (int, str)):
                        return int(emp)
    except Exception:
        pass
    
    return 0


def find_career_page(base_url: str) -> str | None:
    html = fetch_page(base_url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, "html.parser")
    
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        link_text = safe_text(link.get_text(strip=True)).lower()
        href_lower = href.lower()
        
        for path in CAREER_PATHS:
            if path in href_lower:
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    log.debug("Career link found in nav: %s", full_url)
                    return full_url
        
        if any(kw in link_text for kw in ["kariyer", "iş ilan", "career", "jobs", "join us", "çalışma hayatı", "ik", "insan kaynaklari"]):
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                log.debug("Career link found by text: %s", full_url)
                return full_url
    
    return None


def find_about_page(base_url: str) -> str | None:
    for path in ABOUT_PATHS:
        test_url = urljoin(base_url, path)
        html = fetch_page(test_url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            text = safe_text(soup.get_text(" ", strip=True)).lower()
            if any(kw in text for kw in ["hakkımızda", "hakkimizda", "about us", "vizyon", "misyon", "kurumsal", "company", "firma", "hakkind"]):
                log.debug("About page found: %s", test_url)
                return test_url
    return None
def process_company(company_id: str, website: str) -> dict[str, Any]:
    result = {
        "company_id": company_id,
        "job_postings_count": 0,
        "employee_count_estimate": 0,
        "career_page_url": None,
        "about_page_url": None,
        "checked_at": datetime.now().isoformat(),
    }
    
    if not website:
        return result
    
    if not website.startswith(("http://", "https://")):
        website = "https://" + website
    
    skip_domains = ["osp.com.tr", "ostim.org.tr", "isim.org.tr", "ostimonline.com", 
                    "ostimistihdam.com", "facebook.com", "linkedin.com", "twitter.com", "x.com", "instagram.com"]
    if any(d in website.lower() for d in skip_domains):
        return result
    
    try:
        career_url = find_career_page(website)
        if not career_url:
            for path in ["/kariyer", "/career", "/is-ilanlari", "/jobs"]:
                test_url = urljoin(website, path)
                html = fetch_page(test_url)
                if html:
                    soup = BeautifulSoup(html, "html.parser")
                    text = safe_text(soup.get_text(" ", strip=True)).lower()
                    if any(kw in text for kw in JOB_KEYWORDS):
                        career_url = test_url
                        break
        
        if career_url:
            result["career_page_url"] = career_url
            html = fetch_page(career_url)
            if html:
                result["job_postings_count"] = extract_job_count(html, website)
        
        about_url = find_about_page(website)
        if about_url:
            result["about_page_url"] = about_url
            html = fetch_page(about_url)
            if html:
                result["employee_count_estimate"] = extract_employee_count(html)
        
        if result["employee_count_estimate"] == 0:
            html = fetch_page(website)
            if html:
                result["employee_count_estimate"] = extract_employee_count(html)
    
    except Exception as e:
        log.error("Error processing %s (%s): %s", company_id, website, e)
    
    return result


def run_job_postings_scraper(limit: int | None = None, offset: int = 0) -> dict[str, int]:
    engine = get_engine()
    stats = {"processed": 0, "jobs_found": 0, "employees_found": 0, "errors": 0}
    
    with engine.begin() as conn:
        query = """
            SELECT company_id, website_domain 
            FROM companies 
            WHERE website_domain IS NOT NULL AND website_domain != ''
            ORDER BY company_id
            LIMIT :lim OFFSET :off
        """
        rows = conn.execute(text(query), {"lim": limit or 10000, "off": offset}).mappings().all()
        
        if not rows:
            log.info("İşlenecek şirket yok")
            return stats
        
        log.info("Toplam %d şirket işlenecek (limit=%s, offset=%d)", len(rows), limit, offset)
        
        for i, row in enumerate(rows):
            company_id = row["company_id"]
            website = row["website_domain"]
            
            try:
                result = process_company(company_id, website)
                
                conn.execute(text("""
                    UPDATE companies SET
                        job_postings_count = :jobs,
                        employee_count_estimate = :emps,
                        job_postings_last_checked = :checked,
                        employee_count_last_checked = :checked
                    WHERE company_id = :cid
                """), {
                    "jobs": result["job_postings_count"],
                    "emps": result["employee_count_estimate"],
                    "checked": result["checked_at"],
                    "cid": company_id,
                })
                
                if result["job_postings_count"] > 0:
                    stats["jobs_found"] += 1
                if result["employee_count_estimate"] > 0:
                    stats["employees_found"] += 1
                stats["processed"] += 1
                
                if (i + 1) % 20 == 0:
                    log.info("İlerleme: %d/%d - Jobs: %d, Emps: %d, Errors: %d", 
                            i + 1, len(rows), stats["jobs_found"], stats["employees_found"], stats["errors"])
                
                time.sleep(0.6)
                
            except Exception as e:
                stats["errors"] += 1
                log.error("Error processing %s: %s", company_id, e)
    
    return stats


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Job postings & employee count scraper")
    parser.add_argument("--limit", type=int, default=50, help="Max companies to process")
    parser.add_argument("--offset", type=int, default=0, help="Offset for pagination")
    args = parser.parse_args()
    
    log.info("Starting job postings scraper (limit=%s, offset=%d)", args.limit, args.offset)
    stats = run_job_postings_scraper(limit=args.limit, offset=args.offset)
    log.info("Done: %s", json.dumps(stats, ensure_ascii=False))
    print(json.dumps(stats, ensure_ascii=False, indent=2))
