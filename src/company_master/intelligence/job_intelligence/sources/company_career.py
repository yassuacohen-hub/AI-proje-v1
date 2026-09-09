# -*- coding: utf-8 -*-
"""Job Intelligence — Şirket Kariyer Sayfaları Scraper.
 
Mevcut companies.website_domain'lerden /kariyer, /jobs, /career yollarını keşfeder.
KVKK güvenli: Şirket kendi sitesindeki veriyi toplar.
"""
from __future__ import annotations

import logging
import re
import time
from datetime import datetime
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .base import BaseJobSource, ScrapedJob, CAREER_PATHS, JOB_KEYWORDS

logger = logging.getLogger(__name__)


class CompanyCareerSource(BaseJobSource):
    """Şirketlerin kendi kariyer sayfalarından iş ilanı çeken scraper."""
    
    def __init__(self):
        super().__init__(
            source_name="company-career-pages",
            domain=None,  # Dinamik: her şirket için farklı domain
            min_interval=1.5  # Şirket siteleri için daha nazik
        )
        self.companies_cache: list[dict[str, Any]] = []
    
    def load_companies(self, limit: int | None = None) -> list[dict[str, Any]]:
        """DB'den website_domain'i olan şirketleri yükle."""
        from sqlalchemy import text
        from company_master.db.connection import get_engine
        
        engine = get_engine()
        query = '''
            SELECT company_id, legal_name, website_domain
            FROM companies 
            WHERE website_domain IS NOT NULL AND website_domain != '''
            ORDER BY company_id
        '''
        if limit:
            query += f' LIMIT {limit}'
        
        with engine.connect() as conn:
            rows = conn.execute(text(query)).mappings().all()
        
        companies = []
        for row in rows:
            website = row['website_domain'].strip()
            if not website.startswith(('http://', 'https://')):
                website = 'https://' + website
            
            # Placeholder domainleri atla
            skip_domains = [
                'osp.com.tr', 'ostim.org.tr', 'isim.org.tr', 'ostimonline.com',
                'ostimistihdam.com', 'ostimradyo.com', 'facebook.com', 'linkedin.com',
                'twitter.com', 'x.com', 'instagram.com', 'youtube.com'
            ]
            if any(d in website.lower() for d in skip_domains):
                continue
            
            companies.append({
                'company_id': str(row['company_id']),
                'legal_name': row['legal_name'],
                'website_domain': website
            })
        
        self.companies_cache = companies
        logger.info('[%s] %d şirket yüklendi (placeholder atlandı)', self.source_name, len(companies))
        return companies
    
    def discover_job_urls(self, max_pages: int = 10) -> list[str]:
        """Tüm şirketler için kariyer sayfası URL'lerini keşfet."""
        if not self.companies_cache:
            self.load_companies()
        
        urls = []
        for company in self.companies_cache:
            career_url = self._find_career_page(company['website_domain'])
            if career_url:
                urls.append(career_url)
                logger.debug('[%s] %s -> %s', self.source_name, company['legal_name'][:50], career_url)
        
        logger.info('[%s] Toplam %d kariyer sayfası keşfedildi', self.source_name, len(urls))
        return urls[:max_pages] if max_pages else urls
    
    def _find_career_page(self, base_url: str) -> str | None:
        """Şirket sitesinden kariyer sayfasını bul."""
        # 1. Ana sayfadan navigasyon linklerinde ara
        html = self._fetch(base_url)
        if not html:
            return None
        
        soup = self._parse_html(html)
        
        # Navigasyon linklerinde kariyer yollarını ara
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            link_text = self._safe_text(link.get_text(strip=True)).lower()
            href_lower = href.lower()
            
            for path in CAREER_PATHS:
                if path in href_lower:
                    full_url = urljoin(base_url, href)
                    if self._same_domain(base_url, full_url):
                        logger.debug('[%s] Navigasyonda kariyer linki: %s', self.source_name, full_url)
                        return full_url
            
            # Link metninde kariyer anahtar kelimeleri
            if any(kw in link_text for kw in ['kariyer', 'iş ilan', 'career', 'jobs', 'join us', 'çalışma hayatı', 'ik', 'insan kaynaklari', 'pozisyonlar']):
                full_url = urljoin(base_url, href)
                if self._same_domain(base_url, full_url):
                    logger.debug('[%s] Link metninde kariyer: %s', self.source_name, full_url)
                    return full_url
        
        # 2. Doğrudan yaygın yolları dene
        for path in ['/kariyer', '/career', '/jobs', '/is-ilanlari', '/isbasvuru', '/pozisyonlar', '/acik-pozisyonlar']:
            test_url = urljoin(base_url, path)
            html = self._fetch(test_url)
            if html:
                soup = self._parse_html(html)
                text = self._safe_text(soup.get_text(' ', strip=True)).lower()
                if any(kw in text for kw in JOB_KEYWORDS):
                    logger.debug('[%s] Doğrudan path Kariyer: %s', self.source_name, test_url)
                    return test_url
        
        return None
    
    def _same_domain(self, url1: str, url2: str) -> bool:
        """İki URL aynı domain mi?"""
        return urlparse(url1).netloc == urlparse(url2).netloc
    
    def parse_job_detail(self, html: str, url: str) -> ScrapedJob | None:
        """Kariyer sayfasından iş ilanlarını parse et (liste sayfası)."""
        soup = self._parse_html(html)
        text = self._safe_text(soup.get_text(' ', strip=True)).lower()
        
        # Sayfa iş ilanı liste sayfası mı kontrol et
        if not any(kw in text for kw in JOB_KEYWORDS):
            return None
        
        # İlan kartlarını bul
        job_cards = []
        selectors = [
            'div[class*="job"]', 'li[class*="job"]', 'article[class*="job"]',
            'div[class*="career"]', 'li[class*="career"]',
            'div[class*="position"]', 'li[class*="position"]',
            'div[class*="ilan"]', 'li[class*="ilan"]',
            'div[class*="pozisyon"]', 'li[class*="pozisyon"]',
            '.job-list li', '.career-list li', '.positions li',
            'div[class*="listing"]', 'li[class*="listing"]',
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                if len(elements) > len(job_cards):
                    job_cards = elements
            except Exception:
                pass
        
        if not job_cards:
            # Fallback: tüm linklerde iş ilanı anahtar kelimesi olanları topla
            for link in soup.find_all('a', href=True):
                link_text = self._safe_text(link.get_text(strip=True)).lower()
                if any(kw in link_text for kw in JOB_KEYWORDS):
                    job_cards.append(link)
        
        if not job_cards:
            return None
        
        # İlk ilandan örnek veri çıkar (liste sayfası olduğu için tek job dönüyoruz)
        # Gerçek implementasyonda her kart için ayrı ScrapedJob döndürülmeli
        first_card = job_cards[0]
        card_text = self._safe_text(first_card.get_text(' ', strip=True))
        card_html = str(first_card)
        
        # Şirket adını URL'den tahmin et
        parsed = urlparse(url)
        company_name = parsed.netloc.replace('www.', '').split('.')[0].title()
        
        return ScrapedJob(
            source_name=self.source_name,
            source_url=url,
            external_id=None,
            title=f"{company_name} - Kariyer Sayfası ({len(job_cards)} ilan)",
            description=card_text[:500],
            department=None,
            seniority_level=None,
            location_city=None,
            location_country='Türkiye',
            employment_type=None,
            remote_type=None,
            technologies=self._extract_technologies(card_html),
            salary_min=None,
            salary_max=None,
            salary_currency='TRY',
            posted_at=None,
            expired_at=None,
            raw_data={
                'career_page_url': url,
                'job_cards_found': len(job_cards),
                'company_domain': parsed.netloc,
            }
        )
    
    def run_full_scrape(self, max_pages: int = 100, output_file: str | None = None) -> list[ScrapedJob]:
        """Tüm şirketler için kariyer sayfalarını tara.
        
        Args:
            max_pages: Maksimum şirket sayısı (her şirket 1 sayfa = 1 kariyer sayfası)
            output_file: Çıktı dosyası
        """
        logger.info('[%s] Şirket kariyer sayfaları scrape başlıyor (max_companies=%d)', self.source_name, max_pages)
        
        if not self.companies_cache:
            self.load_companies(limit=max_pages)
        
        jobs: list[ScrapedJob] = []
        processed = 0
        
        for company in self.companies_cache[:max_pages]:
            career_url = self._find_career_page(company['website_domain'])
            if not career_url:
                continue
            
            html = self._fetch(career_url)
            if not html:
                continue
            
            job = self.parse_job_detail(html, career_url)
            if job:
                # company_id'yi raw_data'ya ekle
                job.raw_data['company_id'] = company['company_id']
                job.raw_data['company_name'] = company['legal_name']
                jobs.append(job)
            
            processed += 1
            if processed % 50 == 0:
                logger.info('[%s] İlerleme: %d/%d şirket işlendi, %d ilan bulundu', 
                           self.source_name, processed, len(self.companies_cache[:max_pages]), len(jobs))
            
            time.sleep(0.5)  # Nazik ol
        
        logger.info('[%s] Scrape tamamlandı: %d şirket işlendi, %d kariyer sayfası bulundu', 
                   self.source_name, processed, len(jobs))
        
        if output_file and jobs:
            self._save_jsonl(jobs, output_file)
        
        return jobs
