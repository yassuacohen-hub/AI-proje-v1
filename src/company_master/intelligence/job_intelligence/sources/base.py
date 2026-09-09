# -*- coding: utf-8 -*-
"""Job Intelligence — Temel kaynak (scraper) sınıfı."""
from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from company_master.utils.scraping_permission_router import get_router

ROOT = Path(__file__).resolve().parents[4]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

# Ortak User-Agent
USER_AGENT = "OSINT-JobIntelligence/1.0 (+Ankara B2B Company Master)"

# Kavram filtreleri
CAREER_PATHS = [
    "/kariyer", "/kariyer/", "/is-ilanlari", "/is-ilanlari/", "/isbasvuru",
    "/is-basvuru", "/basvuru", "/calisma-hayati", "/calisma-hayati/",
    "/insan-kaynaklari", "/ik", "/career", "/careers", "/jobs", "/job",
    "/join-us", "/joinus", "/work-with-us", "/workwithus", "/pozisyonlar",
    "/acik-pozisyonlar", "/acik-pozisyon", "/yeni-is", "/yeni-is/",
]

JOB_KEYWORDS = [
    "iş ilan", "açık pozisyon", "kariyer fırsat", "job opening", "vacancy",
    "positions", "kariera", "iş fırsatı", "yeni takım", "join us", "join our team",
    "başvuru", "apply now", "işe alım", "pozisyonlar", "acik pozisyon",
]

SENIORITY_KEYWORDS = {
    "junior": ["junior", "jr.", "başlangıç", "entry", "0-1 yıl", "0-2 yıl"],
    "mid": ["mid", "orta", "2-4 yıl", "3-5 yıl", "experienced"],
    "senior": ["senior", "sr.", "uzman", "lead", "5+ yıl", "7+ yıl", "10+ yıl"],
    "lead": ["lead", "team lead", "tech lead", "takım lideri"],
    "manager": ["manager", "müdür", "yönetici", "engineering manager"],
    "director": ["director", "direktör", "vp", "vice president"],
    "c-level": ["cto", "cio", "cfo", "ceo", "chief technology", "chief information"],
}

DEPARTMENT_KEYWORDS = {
    "engineering": ["engineering", "yazılım", "software", "developer", "developer", "backend", "frontend", "fullstack", "devops", "data", "ml", "ai", "platform"],
    "sales": ["sales", "satış", "account executive", "business development", "bd", "müşteri", "customer success"],
    "marketing": ["marketing", "pazarlama", "growth", "seo", "sem", "content", "marka"],
    "hr": ["hr", "human resources", "insan kaynakları", "recruiting", "talent acquisition", "i̇şe alım"],
    "finance": ["finance", "finans", "muhasebe", "accounting", "tax", "vergi", "treasury"],
    "product": ["product", "ürün", "product manager", "pm", "product owner"],
    "design": ["design", "tasarım", "ui", "ux", "user experience", "user interface", "graphic"],
    "operations": ["operations", "operasyon", "lojistik", "supply chain", "tedarik"],
    "it": ["it", "system", "network", "security", "siber", "infrastructure", "altyapı"],
}


@dataclass
class ScrapedJob:
    """Kazınan iş ilanı verisi."""
    source_name: str
    source_url: str
    external_id: str | None
    title: str
    description: str | None
    department: str | None
    seniority_level: str | None
    location_city: str | None
    location_country: str
    employment_type: str | None
    remote_type: str | None
    technologies: list[str]
    salary_min: int | None
    salary_max: int | None
    salary_currency: str
    posted_at: datetime | None
    expired_at: datetime | None
    raw_data: dict[str, Any]


class BaseJobSource(ABC):
    """Tüm iş ilanı kaynakları için temel sınıf.
    
    Permission Router + Rate Limit + KVKK uyumlu.
    """
    
    def __init__(self, source_name: str, domain: str | None = None, min_interval: float = 2.0):
        self.source_name = source_name
        self.domain = domain
        self.min_interval = min_interval
        self._last_request: float = 0.0
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.router = get_router()
    
    def _rate_limit(self) -> None:
        """Domain bazlı rate limiting."""
        if self.domain:
            self.router.rate_limit(self.domain)
        else:
            now = time.time()
            wait = max(0.0, self.min_interval - (now - self._last_request))
            if wait > 0:
                time.sleep(wait)
            self._last_request = time.time()
    
    def _check_permission(self, url: str) -> bool:
        """İzin kontrolü (robots.txt + KVKK)."""
        if not self.domain:
            return True
        decision = self.router.check(url)
        if not decision.allowed:
            logger.warning("[%s] İzin reddedildi: %s - %s", self.source_name, url, decision.reason)
            return False
        return True
    
    def _fetch(self, url: str, timeout: int = 15) -> str | None:
        """Sayfa çek (izin + rate limit + encoding düzeltme)."""
        if not self._check_permission(url):
            return None
        
        self._rate_limit()
        
        try:
            resp = self.session.get(url, timeout=timeout, verify=False, allow_redirects=True)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"
            return resp.text
        except requests.RequestException as e:
            logger.debug("[%s] Fetch hatası %s: %s", self.source_name, url, e)
            return None
    
    def _parse_html(self, html: str) -> BeautifulSoup:
        """HTML parse et."""
        return BeautifulSoup(html, "html.parser")
    
    def _safe_text(self, text: str | None) -> str:
        """Güvenli metin işleme (Türkçe karakterler için)."""
        if not text:
            return ""
        try:
            return text.encode("utf-8", errors="ignore").decode("utf-8")
        except Exception:
            return text
    
    def _extract_technologies(self, text: str) -> list[str]:
        """Metinden teknoloji çıkar (basit keyword matching)."""
        tech_keywords = [
            "python", "java", "javascript", "typescript", "go", "rust", "c#", "c++", "php", "ruby",
            "react", "vue", "angular", "svelte", "next.js", "nuxt", "django", "flask", "fastapi",
            "spring", "node.js", "express", "nestjs", "laravel", "rails",
            "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform",
            "ansible", "jenkins", "gitlab", "github actions", "ci/cd", "prometheus", "grafana",
            "kafka", "rabbitmq", "redis", "postgresql", "mysql", "mongodb", "elasticsearch",
            "spark", "hadoop", "airflow", "dbt", "snowflake", "bigquery", "redshift",
            "pytorch", "tensorflow", "keras", "scikit-learn", "pandas", "numpy",
            "microservices", "rest", "graphql", "grpc", "api", "sql", "nosql",
        ]
        found = []
        text_lower = text.lower()
        for tech in tech_keywords:
            if tech in text_lower:
                found.append(tech)
        return list(set(found))
    
    def _extract_seniority(self, text: str) -> str | None:
        """Metinden kıdem seviyesi çıkar."""
        text_lower = text.lower()
        for level, keywords in SENIORITY_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    return level
        return None
    
    def _extract_department(self, text: str) -> str | None:
        """Metinden departman çıkar."""
        text_lower = text.lower()
        for dept, keywords in DEPARTMENT_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    return dept
        return None
    
    def _normalize_url(self, base_url: str, href: str) -> str | None:
        """URL normalize et."""
        try:
            full = urljoin(base_url, href)
            parsed = urlparse(full)
            if parsed.scheme in ("http", "https") and parsed.netloc:
                return full
        except Exception:
            pass
        return None
    
    @abstractmethod
    def discover_job_urls(self, max_pages: int = 10) -> list[str]:
        """İş ilanı URL'lerini keşfet (liste sayfaları)."""
        pass
    
    @abstractmethod
    def parse_job_detail(self, html: str, url: str) -> ScrapedJob | None:
        """İş ilanı detay sayfasını parse et."""
        pass
    
    def run_full_scrape(self, max_pages: int = 10, output_file: str | None = None) -> list[ScrapedJob]:
        """Tam scrape işlemini çalıştır."""
        logger.info("[%s] Tam scrape başlıyor (max_pages=%d)", self.source_name, max_pages)
        
        urls = self.discover_job_urls(max_pages)
        logger.info("[%s] %d ilan URL'si keşfedildi", self.source_name, len(urls))
        
        jobs: list[ScrapedJob] = []
        for i, url in enumerate(urls):
            html = self._fetch(url)
            if not html:
                continue
            
            job = self.parse_job_detail(html, url)
            if job:
                jobs.append(job)
            
            if (i + 1) % 20 == 0:
                logger.info("[%s] İlerleme: %d/%d", self.source_name, i + 1, len(urls))
        
        logger.info("[%s] Scrape tamamlandı: %d ilan", self.source_name, len(jobs))
        
        if output_file and jobs:
            self._save_jsonl(jobs, output_file)
        
        return jobs
    
    def _save_jsonl(self, jobs: list[ScrapedJob], output_file: str) -> None:
        """JSONL olarak kaydet."""
        import json
        out_path = ROOT / output_file
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(out_path, "w", encoding="utf-8") as f:
            for job in jobs:
                data = {
                    "source_name": job.source_name,
                    "source_url": job.source_url,
                    "external_id": job.external_id,
                    "title": job.title,
                    "description": job.description,
                    "department": job.department,
                    "seniority_level": job.seniority_level,
                    "location_city": job.location_city,
                    "location_country": job.location_country,
                    "employment_type": job.employment_type,
                    "remote_type": job.remote_type,
                    "technologies": job.technologies,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "salary_currency": job.salary_currency,
                    "posted_at": job.posted_at.isoformat() if job.posted_at else None,
                    "expired_at": job.expired_at.isoformat() if job.expired_at else None,
                    "raw_data": job.raw_data,
                    "collected_at": datetime.now().isoformat(),
                }
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        
        logger.info("[%s] %d ilan %s dosyasına yazıldı", self.source_name, len(jobs), output_file) 
