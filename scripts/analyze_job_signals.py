#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Job Signals Analyzer — İş ilanlarından ticari sinyaller çıkarır.

Post-scrape workflow Adım 6 olarak çalışır.
company_signals tablosunu doldurur.
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import text
from company_master.db.connection import get_engine

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "analyze_job_signals.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("analyze_job_signals")

# Sinyal eşik değerleri
THRESHOLDS = {
    "hiring_surge_30d": 5,      # 30 günde 5+ ilan -> growth
    "hiring_surge_90d": 15,     # 90 günde 15+ ilan -> growth
    "new_city_threshold": 1,    # Yeni şehir -> geo_expansion
    "new_dept_threshold": 1,    # Yeni departman -> org_change
    "executive_hiring": 1,      # Yönetici işe alımı -> investment/org_change
    "tech_modernization": 2,    # Yeni tech stack -> tech_transformation
    "dept_growth_rate": 0.5,    # Departman büyüme oranı %50+ -> growth
    "risk_drop_30d": 0,         # 30 günde ilan yok -> risk (eğer önceki dönemde varsa)
    "risk_drop_90d": 0,         # 90 günde ilan yok -> risk
}


def get_db_engine():
    return get_engine()


def analyze_company_signals(company_id: str, lookback_days: int = 180) -> list[dict[str, Any]]:
    """Tek bir şirket için sinyalleri analiz et."""
    signals = []
    engine = get_db_engine()
    
    with engine.connect() as conn:
        # İş ilanlarını çek
        rows = conn.execute(text("""
            SELECT 
                job_posting_id, title, department, seniority_level, location_city,
                technologies, posted_at, collected_at
            FROM job_postings
            WHERE company_id = :cid
            AND posted_at >= NOW() - INTERVAL '%s days'
            ORDER BY posted_at
        """ % lookback_days), {"cid": company_id}).mappings().all()
        
        if not rows:
            return signals
        
        # Zaman pencereleri
        now = datetime.now()
        cutoff_30d = now - timedelta(days=30)
        cutoff_90d = now - timedelta(days=90)
        
        postings_30d = [r for r in rows if r["posted_at"] and r["posted_at"] >= cutoff_30d]
        postings_90d = [r for r in rows if r["posted_at"] and r["posted_at"] >= cutoff_90d]
        
        # --- 1. BÜYÜME SİNYALLERİ ---
        
        # 1a. İşe alım patlaması (30 gün)
        if len(postings_30d) >= THRESHOLDS["hiring_surge_30d"]:
            signals.append({
                "company_id": company_id,
                "signal_type": "growth",
                "signal_subtype": "hiring_surge_30d",
                "score": min(50 + len(postings_30d) * 3, 100),
                "confidence": 80,
                "evidence": {
                    "postings_count": len(postings_30d),
                    "period_days": 30,
                    "job_posting_ids": [str(r["job_posting_id"]) for r in postings_30d],
                    "titles": [r["title"] for r in postings_30d[:10]],
                }
            })
        
        # 1b. İşe alım trendi (90 gün)
        if len(postings_90d) >= THRESHOLDS["hiring_surge_90d"]:
            signals.append({
                "company_id": company_id,
                "signal_type": "growth",
                "signal_subtype": "hiring_surge_90d",
                "score": min(40 + len(postings_90d) * 2, 90),
                "confidence": 85,
                "evidence": {
                    "postings_count": len(postings_90d),
                    "period_days": 90,
                    "job_posting_ids": [str(r["job_posting_id"]) for r in postings_90d],
                }
            })
        
        # 1c. Yönetici/Kıdemli işe alımı
        executive_postings = [r for r in rows if r["seniority_level"] in ("director", "c-level", "vp", "head", "manager")]
        if len(executive_postings) >= THRESHOLDS["executive_hiring"]:
            signals.append({
                "company_id": company_id,
                "signal_type": "investment",
                "signal_subtype": "executive_hiring",
                "score": min(60 + len(executive_postings) * 10, 195),
                "confidence": 90,
                "evidence": {
                    "executive_count": len(executive_postings),
                    "titles": [r["title"] for r in executive_postings],
                    "seniority_levels": [r["seniority_level"] for r in executive_postings],
                    "job_posting_ids": [str(r["job_posting_id"]) for r in executive_postings],
                }
            })
        
        # --- 2. COĞRAFİ GENİŞLEME ---
        
        # Şehir bazlı dağılım
        city_counts = defaultdict(int)
        city_first_seen = {}
        for r in rows:
            if r["location_city"]:
                city = r["location_city"].strip()
                city_counts[city] += 1
                if city not in city_first_seen or (r["posted_at"] and r["posted_at"] < city_first_seen[city]):
                    city_first_seen[city] = r["posted_at"]
        
        # Yeni şehirler (son 90 günde ilk kez görülen)
        for city, first_seen in city_first_seen.items():
            if first_seen and first_seen >= cutoff_90d:
                signals.append({
                    "company_id": company_id,
                    "signal_type": "geo_expansion",
                    "signal_subtype": "new_city",
                    "score": 50,
                    "confidence": 75,
                    "evidence": {
                        "city": city,
                        "first_seen": first_seen.isoformat() if first_seen else None,
                        "total_postings_in_city": city_counts[city],
                    }
                })
        
        # --- 3. ORGANİZASYON DEĞİŞİMİ ---
        
        # Departman bazlı dağılım
        dept_counts = defaultdict(int)
        dept_first_seen = {}
        for r in rows:
            if r["department"]:
                dept = r["department"].strip().lower()
                dept_counts[dept] += 1
                if dept not in dept_first_seen or (r["posted_at"] and r["posted_at"] < dept_first_seen[dept]):
                    dept_first_seen[dept] = r["posted_at"]
        
        # Yeni departmanlar
        for dept, first_seen in dept_first_seen.items():
            if first_seen and first_seen >= cutoff_90d:
                signals.append({
                    "company_id": company_id,
                    "signal_type": "org_change",
                    "signal_subtype": "new_department",
                    "score": 40,
                    "confidence": 70,
                    "evidence": {
                        "department": dept,
                        "first_seen": first_seen.isoformat() if first_seen else None,
                        "postings_count": dept_counts[dept],
                    }
                })
        
        # Departman büyümesi (mevcut departmandaki artış)
        # Önceki dönem (90-180 gün) vs son 90 gün karşılaştırması
        cutoff_180d = now - timedelta(days=180)
        prev_period = [r for r in rows if r["posted_at"] and cutoff_180d <= r["posted_at"] < cutoff_90d]
        prev_dept_counts = defaultdict(int)
        for r in prev_period:
            if r["department"]:
                prev_dept_counts[r["department"].strip().lower()] += 1
        
        for dept, curr_count in dept_counts.items():
            prev_count = prev_dept_counts.get(dept, 0)
            if prev_count > 0 and curr_count >= prev_count * (1 + THRESHOLDS["dept_growth_rate"]):
                growth_rate = (curr_count - prev_count) / prev_count
                signals.append({
                    "company_id": company_id,
                    "signal_type": "growth",
                    "signal_subtype": "department_growth",
                    "score": min(30 + growth_rate * 50, 80),
                    "confidence": 70,
                    "evidence": {
                        "department": dept,
                        "previous_count": prev_count,
                        "current_count": curr_count,
                        "growth_rate": round(growth_rate * 100, 1),
                    }
                })
        
        # --- 4. TEKNOLOJİ DÖNÜŞÜMÜ ---
        
        # Teknoloji trendleri
        all_techs = []
        tech_timeline = defaultdict(list)  # tech -> [(date, count)]
        
        for r in rows:
            if r["technologies"] and isinstance(r["technologies"], list):
                for tech in r["technologies"]:
                    all_techs.append(tech.lower().strip())
                    if r["posted_at"]:
                        tech_timeline[tech.lower().strip()].append(r["posted_at"])
        
        tech_counts = defaultdict(int)
        for tech in all_techs:
            tech_counts[tech] += 1
        
        # Modern tech stack tespiti (cloud, k8s, modern languages)
        modern_techs = {"kubernetes", "aws", "azure", "gcp", "docker", "terraform",
                       "kafka", "spark", "pytorch", "tensorflow", "react", "vue",
                       "next.js", "fastapi", "golang", "rust", "typescript"}
        
        modern_count = sum(1 for tech in tech_counts if tech in modern_techs)
        if modern_count >= THRESHOLDS["tech_modernization"]:
            signals.append({
                "company_id": company_id,
                "signal_type": "tech_transformation",
                "signal_subtype": "modern_stack_adoption",
                "score": min(40 + modern_count * 5, 85),
                "confidence": 75,
                "evidence": {
                    "modern_technologies": [t for t in tech_counts if t in modern_techs],
                    "total_unique_techs": len(tech_counts),
                    "top_techs": dict(sorted(tech_counts.items(), key=lambda x: -x[1])[:10]),
                }
            })
        
        # Legacy -> Modern geçiş tespiti
        legacy_techs = {".net framework", "jquery", "angularjs", "php 5", "java 8", "on-premise"}
        legacy_found = [t for t in tech_counts if any(lt in t for lt in legacy_techs)]
        modern_found = [t for t in tech_counts if t in modern_techs]
        
        if legacy_found and modern_found:
            signals.append({
                "company_id": company_id,
                "signal_type": "tech_transformation",
                "signal_subtype": "legacy_to_modern_migration",
                "score": 65,
                "confidence": 80,
                "evidence": {
                    "legacy_technologies": legacy_found,
                    "modern_technologies": modern_found,
                    "transition_indicator": True,
                }
            })
        
        # --- 5. YATIRIM SİNYALLERİ ---
        
        # Ar-Ge / Ürün ekibi büyümesi
        rd_depts = {"r&d", "research", "ar-ge", "product", "ürün", "innovation", "yenilik"}
        rd_postings = [r for r in rows if r["department"] and r["department"].strip().lower() in rd_depts]
        if len(rd_postings) >= 2:
            signals.append({
                "company_id": company_id,
                "signal_type": "investment",
                "signal_subtype": "rd_team_expansion",
                "score": min(50 + len(rd_postings) * 5, 90),
                "confidence": 80,
                "evidence": {
                    "rd_postings_count": len(rd_postings),
                    "titles": [r["title"] for r in rd_postings],
                    "job_posting_ids": [str(r["job_posting_id"]) for r in rd_postings],
                }
            })
        
        # Business Development / Satış genişlemesi
        bd_depts = {"sales", "satış", "business development", "bd", "account", "musteri", "customer success"}
        bd_postings = [r for r in rows if r["department"] and r["department"].strip().lower() in bd_depts]
        if len(bd_postings) >= 3:
            signals.append({
                "company_id": company_id,
                "signal_type": "investment",
                "signal_subtype": "sales_expansion",
                "score": min(40 + len(bd_postings) * 3, 85),
                "confidence": 75,
                "evidence": {
                    "bd_postings_count": len(bd_postings),
                    "titles": [r["title"] for r in bd_postings],
                }
            })
        
        # --- 6. RİSK SİNYALLERİ ---
        
        # İşe alım durması (önceki dönemde ilan varsa ama son 90 günde yok)
        total_prev = len(prev_period)
        total_curr = len(postings_90d)
        
        if total_prev > 0 and total_curr == 0:
            signals.append({
                "company_id": company_id,
                "signal_type": "risk",
                "signal_subtype": "hiring_freeze",
                "score": 70,
                "confidence": 80,
                "evidence": {
                    "previous_90d_count": total_prev,
                    "current_90d_count": 0,
                    "message": "Son 90 günde iş ilanı yok, önceki dönemde aktif idi",
                }
            })
        elif total_prev > 0 and total_curr < total_prev * 0.3:
            signals.append({
                "company_id": company_id,
                "signal_type": "risk",
                "signal_subtype": "hiring_slowdown",
                "score": 50,
                "confidence": 70,
                "evidence": {
                    "previous_90d_count": total_prev,
                    "current_90d_count": total_curr,
                    "decline_rate": round((1 - total_curr / total_prev) * 100, 1),
                }
            })
        
        # Teknik ekip azalması
        tech_depts = {"engineering", "it", "devops", "data", "software", "backend", "frontend", "fullstack"}
        tech_prev = len([r for r in prev_period if r["department"] and r["department"].strip().lower() in tech_depts])
        tech_curr = len([r for r in postings_90d if r["department"] and r["department"].strip().lower() in tech_depts])
        
        if tech_prev > 0 and tech_curr == 0:
            signals.append({
                "company_id": company_id,
                "signal_type": "risk",
                "signal_subtype": "tech_team_reduction",
                "score": 75,
                "confidence": 80,
                "evidence": {
                    "previous_tech_postings": tech_prev,
                    "current_tech_postings": 0,
                }
            })
    
    return signals


def save_signals(signals: list[dict[str, Any]]) -> tuple[int, int]:
    """Sinyalleri company_signals tablosuna kaydet."""
    if not signals:
        return 0, 0
    
    engine = get_db_engine()
    inserted = 0
    updated = 0
    
    with engine.begin() as conn:
        for signal in signals:
            try:
                # Mevcut sinyel var mı kontrol et (aynı company + type + subtype + yakın tarih)
                existing = conn.execute(text("""
                    SELECT signal_id FROM company_signals
                    WHERE company_id = :cid
                    AND signal_type = :stype
                    AND signal_subtype = :ssubtype
                    AND detected_at >= NOW() - INTERVAL '30 days'
                    ORDER BY detected_at DESC
                    LIMIT 1
                """), {
                    "cid": signal["company_id"],
                    "stype": signal["signal_type"],
                    "ssubtype": signal["signal_subtype"]
                }).first()
                
                if existing:
                    # Güncelle
                    conn.execute(text("""
                        UPDATE company_signals SET
                            score = :score,
                            confidence = :confidence,
                            evidence = :evidence::jsonb,
                            detected_at = :detected_at,
                            valid_until = :valid_until,
                            metadata = :metadata::jsonb
                        WHERE signal_id = :sid
                    """), {
                        "score": signal["score"],
                        "confidence": signal["confidence"],
                        "evidence": json.dumps(signal["evidence"], ensure_ascii=False),
                        "detected_at": signal.get("detected_at", datetime.now()),
                        "valid_until": signal.get("valid_until"),
                        "metadata": json.dumps(signal.get("metadata", {}), ensure_ascii=False),
                        "sid": existing[0]
                    })
                    updated += 1
                else:
                    # Yeni ekle
                    conn.execute(text("""
                        INSERT INTO company_signals (
                            company_id, signal_type, signal_subtype, score, confidence,
                            evidence, detected_at, valid_until, metadata
                        ) VALUES (
                            :cid, :stype, :ssubtype, :score, :confidence,
                            :evidence::jsonb, :detected_at, :valid_until, :metadata::jsonb
                        )
                    """), {
                        "cid": signal["company_id"],
                        "stype": signal["signal_type"],
                        "ssubtype": signal["signal_subtype"],
                        "score": signal["score"],
                        "confidence": signal["confidence"],
                        "evidence": json.dumps(signal["evidence"], ensure_ascii=False),
                        "detected_at": signal.get("detected_at", datetime.now()),
                        "valid_until": signal.get("valid_until"),
                        "metadata": json.dumps(signal.get("metadata", {}), ensure_ascii=False),
                    })
                    inserted += 1
                    
            except Exception as e:
                log.error("Sinyal kaydetme hatası: %s", e)
    
    return inserted, updated


def run_analysis(limit: int | None = None) -> dict[str, int]:
    """Tüm şirketler için sinyal analizi çalıştır."""
    engine = get_db_engine()
    
    with engine.connect() as conn:
        # İş ilanı olan şirketleri al
        query = """
            SELECT DISTINCT company_id 
            FROM job_postings 
            WHERE company_id IS NOT NULL
        """
        if limit:
            query += f" LIMIT {limit}"
        
        company_ids = [str(r[0]) for r in conn.execute(text(query)).fetchall()]
    
    log.info("%d şirket analiz edilecek", len(company_ids))
    
    stats = {"companies": 0, "signals_generated": 0, "signals_saved": 0, "errors": 0}
    
    for i, company_id in enumerate(company_ids):
        try:
            signals = analyze_company_signals(company_id)
            if signals:
                inserted, updated = save_signals(signals)
                stats["signals_generated"] += len(signals)
                stats["signals_saved"] += inserted + updated
            
            stats["companies"] += 1
            
            if (i + 1) % 100 == 0:
                log.info("İlerleme: %d/%d şirket", i + 1, len(company_ids))
                
        except Exception as e:
            stats["errors"] += 1
            log.error("Şirket %s analiz hatası: %s", company_id, e)
    
    return stats


def main() -> int:
    import sys
    
    log.info("=== Job Signals Analysis Başlatılıyor ===")
    
    try:
        stats = run_analysis()
        
        log.info("=== ANALİZ TAMAMLANDI ===")
        log.info("Şirket: %d, Sinyal Üretilen: %d, Kaydedilen: %d, Hata: %d",
                stats["companies"], stats["signals_generated"], stats["signals_saved"], stats["errors"])
        
        print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
        return 0 if stats["errors"] == 0 else 1
        
    except Exception as e:
        log.exception("Analiz hatası: %s", e)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
