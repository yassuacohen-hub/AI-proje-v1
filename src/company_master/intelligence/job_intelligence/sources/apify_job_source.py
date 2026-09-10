# -*- coding: utf-8 -*-
"""APIFY-02: ApifyJobSource — BaseJobSource uzerinden Apify REST adaptoru.

Bu modul, Apify API'sini OSINT_Scraper_Motoru'na entegrer eder.
ApifyActor calistirilir, dataset sayfalari okunur, ScrapedJob formatina donusurulur.

Temel akis:
1. ApifyJobSource.discover_job_urls() -> Apify Actor run baslatir, dataset URL'lerini getirir
2. ApifyJobSource.parse_job_detail() -> Apify dataset ogelerinden ScrapedJob olusturur
3. run_full_scrape() -> BaseJobSource framework'u uzerinden calisir

Not: PermissionRouter kontrolu yapilmamalidir — Apify bulut platformudur,
domain bazli izin kontrolu gerekmez. Rate limit Apify API tarafindan yonetilir.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from company_master.intelligence.job_intelligence.sources.base import (
    BaseJobSource,
    ScrapedJob,
)
from company_master.intelligence.job_intelligence.sources.apify_client import (
    ApifyClient,
    ApifyError,
)

logger = logging.getLogger(__name__)


class ApifyJobSource(BaseJobSource):
    """Apify Actor'lar uzerinden is ilani kazayan kaynak.
    
    BaseJobSource framework'una uyuyor: _fetch yerine Apify REST API kullanir.
    PermissionRouter kontrolu atlanir (Apify cloud'da calisir).
    """
    
    def __init__(
        self,
        source_name: str,
        actor_id: str,
        domain: str | None = None,
        min_interval: float = 2.0,
        apify_token: str | None = None,
    ) -> None:
        """
        Args:
            source_name: Kaynak adi (ör. "apify-kariyer")
            actor_id: Apify Actor kimligi (ör. "ziyrak/kariyer-scraper")
            domain: Domain bilgisi (opsiyonel, log için)
            min_interval: Minimum istek aralığı (Apify'de kullanılmaz)
            apify_token: Apify API token (varsayılan: APOFY_TOKEN env)
        """
        super().__init__(source_name=source_name, domain=domain, min_interval=min_interval)
        self.actor_id = actor_id
        self.apify_client = ApifyClient(token=apify_token)
        self._current_run_meta: dict[str, Any] | None = None
        self._current_dataset_id: str | None = None
    
    def _start_actor(self, run_input: dict[str, Any] | None = None) -> str:
        """Apify Actor baslatir ve run_id dondurur."""
        run_meta = self.apify_client.start_actor_run(
            actor_id=self.actor_id,
            run_input=run_input or {},
            max_items=100,
            max_total_charge_usd=5.0,
        )
        run_id = run_meta.get("id")
        self._current_run_meta = run_meta
        self._current_dataset_id = (
            run_meta.get("defaultDatasetId")
            or run_meta.get("defaultDatasetId")
        )
        logger.info(
            "[%s] Apify run baslatildi: run_id=%s actor=%s",
            self.source_name, run_id, self.actor_id,
        )
        return run_id
    
    def _fetch_dataset(self, limit: int = 100) -> list[dict[str, Any]]:
        """Apify dataset'ini sayfalari oku."""
        if not self._current_dataset_id:
            raise ApifyError("Dataset kimligi yok. Once _start_actor çağrılmalı.")
        
        items = self.apify_client.fetch_dataset_items(
            dataset_id=self._current_dataset_id,
            max_items=limit,
        )
        logger.info("[%s] %d Apify dataset öğesi okundu", self.source_name, len(items))
        return items
    
    def _apify_item_to_scraped_job(self, item: dict[str, Any]) -> ScrapedJob | None:
        """Apify dataset ogelerini ScrapedJob formatina donustur."""
        try:
            return ScrapedJob(
                source_name=self.source_name,
                source_url=item.get("url", item.get("link", "")),
                external_id=item.get("id", item.get("external_id", None)),
                title=item.get("title", item.get("jobTitle", "")),
                description=item.get("description", item.get("body", "")),
                department=item.get("department", item.get("company", None)),
                seniority_level=None,
                location_city=item.get("city", item.get("location", {}).get("city") if isinstance(item.get("location"), dict) else None),
                location_country="Türkiye",
                employment_type=item.get("employmentType", None),
                remote_type=item.get("remoteType", None),
                technologies=item.get("technologies", []) if isinstance(item.get("technologies"), list) else [],
                salary_min=item.get("salaryMin", item.get("salary_min")),
                salary_max=item.get("salaryMax", item.get("salary_max")),
                salary_currency=item.get("salaryCurrency", "TRY"),
                posted_at=None,
                expired_at=None,
                raw_data=item,
            )
        except Exception as e:
            logger.debug("[%s] Apify item donusturme hatasi: %s", self.source_name, e)
            return None
    
    def discover_job_urls(self, max_pages: int = 10) -> list[str]:
        """Apify Actor calistirir ve ilk sayfa URL'lerini getirir.
        
        Gercek donus: Apify dataset'inden ilk sayfa ID'ler getirilir.
        Sonra parse_job_detail dataset ogelerinden ScrapedJob olusturur.
        """
        run_id = self._start_actor()
        items = self._fetch_dataset(limit=max_pages * 10)
        
        urls = [item.get("url", item.get("link", "")) for item in items if item.get("url") or item.get("link")]
        logger.info("[%s] %d Apify URL'si keşfedildi (run_id=%s)", self.source_name, len(urls), run_id)
        return urls
    
    def parse_job_detail(self, html: str, url: str) -> ScrapedJob | None:
        """Apify dataset ogelerinden ScrapedJob olusturur.
        
        Not: html parametresi Apify context'inde kullanılmaz;
        donusum _fetch_dataset icinde yapilir. Bu metod sadece
        BaseJobSource API'sine uyma amacindadir.
        """
        return None
    
    def run_full_scrape(self, max_pages: int = 10, output_file: str | None = None) -> list[ScrapedJob]:
        """Apify uzerinden tam scrape. BaseJobSource override."""
        logger.info("[%s] Apify scrape baslıyor (max_pages=%d)", self.source_name, max_pages)
        
        run_id = self._start_actor()
        items = self._fetch_dataset(limit=max_pages * 10)
        
        jobs: list[ScrapedJob] = []
        for item in items:
            job = self._apify_item_to_scraped_job(item)
            if job:
                jobs.append(job)
        
        logger.info("[%s] Apify scrape tamamlandı: %d ilan", self.source_name, len(jobs))
        
        if output_file and jobs:
            self._save_jsonl(jobs, output_file)
        
        return jobs


# ---- Pilot / test fonksiyonlari ----

def run_apify_pilot(actor_id: str = "ziyrak/kariyer-scraper", output_file: str = "data/job_intelligence/apify_pilot.jsonl") -> dict[str, Any]:
    """Apify pilot run'u: 10 firma ile test.
    
    Donus:
        {
            "actor_id": str,
            "run_id": str,
            "status": "SUCCEEDED" | "FAILED",
            "items_collected": int,
            "dataset_id": str,
            "output_file": str,
            "timestamp": str
        }
    """
    logger.info("APIFY PILOT baslatiliyor: actor=%s", actor_id)
    
    source = ApifyJobSource(source_name="apify-pilot", actor_id=actor_id)
    run_meta = source._start_actor()
    run_id = run_meta.get("id", "unknown")
    dataset_id = run_meta.get("defaultDatasetId", "")
    
    items = source._fetch_dataset(limit=10)
    
    jobs = []
    for item in items:
        job = source._apify_item_to_scraped_job(item)
        if job:
            jobs.append(job)
    
    if jobs:
        source._save_jsonl(jobs, output_file)
    
    result = {
        "actor_id": actor_id,
        "run_id": run_id,
        "status": "SUCCEEDED" if not _has_error(run_meta) else "FAILED",
        "items_collected": len(jobs),
        "dataset_id": dataset_id,
        "output_file": output_file,
        "timestamp": datetime.now().isoformat(),
    }
    
    logger.info("APIFY PILOT tamamlandi: %s", result)
    return result


def _has_error(run_meta: dict[str, Any]) -> bool:
    """Run metadata'da hata var mi kontrol et."""
    status = run_meta.get("status", "")
    return status not in ("SUCCEEDED", "succeeded") and status != ""