#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Job Postings Ingest Script — JSONL dosyalarını job_postings tablosuna yazar.

Post-scrape workflow Adım 5 olarak çalışır.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import text
from company_master.db.connection import get_engine
from company_master.intelligence.job_intelligence.pipeline.normalizer import CompanyMatcher, MatchResult

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "ingest_job_postings.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("ingest_job_postings")

# İşlenecek kaynak dosyalar
SOURCE_FILES = [
    ("company-career-pages", ROOT / "data" / "job_intelligence" / "company_career_jobs.jsonl"),
    ("iskur", ROOT / "data" / "job_intelligence" / "iskur_jobs.jsonl"),
    ("kariyer-net", ROOT / "data" / "job_intelligence" / "kariyer_net_jobs.jsonl"),
]

BATCH_SIZE = 100


def load_jsonl(file_path: Path) -> list[dict[str, Any]]:
    """JSONL dosyasını yükle."""
    records = []
    if not file_path.exists():
        log.warning("Dosya yok: %s", file_path)
        return records
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                log.warning("Satır %d: JSON parse hatası: %s", line_num, e)
    
    log.info("%s: %d kayıt yüklendi", file_path.name, len(records))
    return records


def parse_datetime(dt_str: str | None) -> datetime | None:
    """ISO format datetime parse et."""
    if not dt_str:
        return None
    try:
        # Zulu time (Z) veya offset (+00:00) handle et
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def prepare_job_record(record: dict[str, Any], matcher: CompanyMatcher, source_name: str) -> dict[str, Any] | None:
    """Ham kaydı DB kayıt formatına çevir."""
    # Şirket eşleştirme
    match_result: MatchResult = matcher.match(
        raw_name=record.get("title") or record.get("company_name"),
        domain=record.get("source_url") or record.get("career_page_url"),
        tax_number=record.get("tax_number"),
        mersis=record.get("mersis")
    )
    
    company_id = match_result.company_id
    
    # Eşleşme yoksa kaynak adından domain çıkararak dene
    if not company_id and record.get("source_url"):
        from company_master.intelligence.job_intelligence.pipeline.normalizer import extract_domain
        domain = extract_domain(record["source_url"])
        if domain:
            match_result = matcher.match(domain=domain)
            company_id = match_result.company_id
    
    # Hala eşleşme yoksa ve raw_data'dan company_id varsa kullan
    if not company_id and record.get("raw_data", {}).get("company_id"):
        try:
            from uuid import UUID
            company_id = UUID(record["raw_data"]["company_id"])
            match_result = MatchResult(
                company_id=company_id,
                matched_name=None,
                match_type="raw_data",
                confidence=90.0,
                details={}
            )
        except Exception:
            pass
    
    # Şirket eşleşmediysine atla (logla ama hata yapma)
    if not company_id:
        log.debug("Eşleşme yok: %s (source=%s)", record.get("title", "")[:50], source_name)
        return None
    
    # Tarih parse et
    posted_at = parse_datetime(record.get("posted_at"))
    expired_at = parse_datetime(record.get("expired_at"))
    collected_at = parse_datetime(record.get("collected_at")) or datetime.now()
    
    # Content hash hesapla (deduplication için)
    import hashlib
    content_parts = [
        str(company_id),
        record.get("title", ""),
        record.get("source_url", ""),
        record.get("description", "")[:200] if record.get("description") else "",
    ]
    content_hash = hashlib.sha256("|".join(content_parts).encode()).hexdigest()[:32]
    
    return {
        "company_id": str(company_id),
        "source_name": source_name,
        "source_url": record.get("source_url", ""),
        "external_id": record.get("external_id"),
        "title": record.get("title", "")[:500],
        "description": record.get("description"),
        "department": record.get("department"),
        "seniority_level": record.get("seniority_level"),
        "location_city": record.get("location_city"),
        "location_country": record.get("location_country", "Türkiye"),
        "employment_type": record.get("employment_type"),
        "remote_type": record.get("remote_type"),
        "technologies": record.get("technologies", []),
        "salary_min": record.get("salary_min"),
        "salary_max": record.get("salary_max"),
        "salary_currency": record.get("salary_currency", "TRY"),
        "posted_at": posted_at,
        "expired_at": expired_at,
        "collected_at": collected_at,
        "content_hash": content_hash,
        "raw_data": record.get("raw_data", {}),
    }


def ingest_job_postings() -> dict[str, int]:
    """Tüm kaynak dosyalarını işle ve DB'ye yaz."""
    matcher = CompanyMatcher(fuzzy_threshold=85.0)
    
    stats = {
        "total_files": 0,
        "total_records": 0,
        "matched": 0,
        "inserted": 0,
        "duplicates": 0,
        "errors": 0,
        "by_source": {},
    }
    
    engine = get_engine()
    
    for source_name, file_path in SOURCE_FILES:
        log.info("İşleniyor: %s (%s)", source_name, file_path)
        stats["total_files"] += 1
        
        records = load_jsonl(file_path)
        if not records:
            continue
        
        stats["total_records"] += len(records)
        source_matched = 0
        source_inserted = 0
        source_duplicates = 0
        source_errors = 0
        
        with engine.begin() as conn:
            batch = []
            
            for record in records:
                try:
                    prepared = prepare_job_record(record, matcher, source_name)
                    if not prepared:
                        continue
                    
                    source_matched += 1
                    batch.append(prepared)
                    
                    if len(batch) >= BATCH_SIZE:
                        inserted, duplicates = _insert_batch(conn, batch)
                        source_inserted += inserted
                        source_duplicates += duplicates
                        batch = []
                        
                except Exception as e:
                    source_errors += 1
                    log.error("Kayıt işleme hatası (%s): %s", record.get("title", "")[:50], e)
            
            # Kalan batch
            if batch:
                inserted, duplicates = _insert_batch(conn, batch)
                source_inserted += inserted
                source_duplicates += duplicates
        
        stats["matched"] += source_matched
        stats["inserted"] += source_inserted
        stats["duplicates"] += source_duplicates
        stats["errors"] += source_errors
        stats["by_source"][source_name] = {
            "records": len(records),
            "matched": source_matched,
            "inserted": source_inserted,
            "duplicates": source_duplicates,
            "errors": source_errors,
        }
        
        log.info("%s tamamlandı: matched=%d, inserted=%d, duplicates=%d, errors=%d",
                source_name, source_matched, source_inserted, source_duplicates, source_errors)
    
    return stats


def _insert_batch(conn, batch: list[dict[str, Any]]) -> tuple[int, int]:
    """Batch insert (ON CONFLICT ile deduplication)."""
    if not batch:
        return 0, 0
    
    inserted = 0
    duplicates = 0
    
    for record in batch:
        try:
            result = conn.execute(text("""
                INSERT INTO job_postings (
                    company_id, source_name, source_url, external_id, title, description,
                    department, seniority_level, location_city, location_country,
                    employment_type, remote_type, technologies, salary_min, salary_max,
                    salary_currency, posted_at, expired_at, collected_at, content_hash, raw_data
                ) VALUES (
                    :company_id, :source_name, :source_url, :external_id, :title, :description,
                    :department, :seniority_level, :location_city, :location_country,
                    :employment_type, :remote_type, :technologies, :salary_min, :salary_max,
                    :salary_currency, :posted_at, :expired_at, :collected_at, :content_hash, :raw_data
                )
                ON CONFLICT (source_name, external_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    department = EXCLUDED.department,
                    seniority_level = EXCLUDED.seniority_level,
                    location_city = EXCLUDED.location_city,
                    location_country = EXCLUDED.location_country,
                    employment_type = EXCLUDED.employment_type,
                    remote_type = EXCLUDED.remote_type,
                    technologies = EXCLUDED.technologies,
                    salary_min = EXCLUDED.salary_min,
                    salary_max = EXCLUDED.salary_max,
                    salary_currency = EXCLUDED.salary_currency,
                    posted_at = EXCLUDED.posted_at,
                    expired_at = EXCLUDED.expired_at,
                    collected_at = EXCLUDED.collected_at,
                    raw_data = EXCLUDED.raw_data,
                    updated_at = NOW()
            """), record)
            
            if result.rowcount > 0:
                inserted += 1
            else:
                duplicates += 1
                
        except Exception as e:
            # Duplicate key violation veya diğer hatalar
            raise
    
    return inserted, duplicates


def main() -> int:
    log.info("=== Job Postings Ingest Başlatılıyor ===")
    
    try:
        stats = ingest_job_postings()
        
        log.info("=== INGEST TAMAMLANDI ===")
        log.info("Dosya: %d, Toplam Kayıt: %d", stats["total_files"], stats["total_records"])
        log.info("Eşleşen: %d, Eklenen: %d, Duplicate: %d, Hata: %d",
                stats["matched"], stats["inserted"], stats["duplicates"], stats["errors"])
        
        for source, s in stats["by_source"].items():
            log.info("  %s: kayıt=%d, eşleşen=%d, eklenen=%d, dup=%d, hata=%d",
                    source, s["records"], s["matched"], s["inserted"], s["duplicates"], s["errors"])
        
        print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
        return 0 if stats["errors"] == 0 else 1
        
    except Exception as e:
        log.exception("Ingest hatası: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main()