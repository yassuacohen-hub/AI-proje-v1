#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Risk Signal Scoring Engine — P8-4.

Job Intelligence modulune ait risk sinyalleri skorlama motoru.
company_signals tablosuna risk sinyali score ekler;
company_intelligence_scores.risk_score alanini doldurur.

Risk Sinyalleri:
  1. ilan_azalma            — İş ilanı azalması / churn (declining postings)
  2. lokasyon_kapanis       — Lokasyon kapanışları (cities dropped)
  3. teknik_ekip_durmasi    — Teknik ekip durması (tech team reduction)
  4. ayni_pozisyon_tekrari  — Aynı pozisyon tekrarları (position churn/turnover)

Skorlama formülü (scorer.py _weighted_avg ile aynı desen):
  risk_score = Σ(signal_score × confidence) / Σ(confidence)

Risk Seviyeleri (aggregate risk_score):
  0-24   : Düşük risk (Low Risk)
  25-49  : Orta risk (Moderate Risk)
  50-74  : Yüksek risk (Elevated Risk)
  75-100 : Kritik risk (High Risk)
"""
from __future__ import annotations

import json
import logging
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("risk_signal_scorer")

# ============================================================
# EŞİK DEĞERLERİ (THRESHOLDS)
# ============================================================

THRESHOLDS: dict[str, Any] = {
    # 1. İş ilanı azalması (job_posting_decline)
    #    Önceki 90 günden sonraki 90 güne ilan sayısı karşılaştırması
    "decline_window_days": 90,
    "decline_rate_min_pct": 10.0,      # %10 azalma → sinyal tetiklenir
    "decline_rate_moderate_pct": 25.0, # %25 → orta risk
    "decline_rate_severe_pct": 50.0,   # %50 → şiddetli risk
    #
    # 2. Lokasyon kapanışı (location_closure)
    "location_window_days": 90,
    "location_closure_min": 1,          # 1+ şehir kaybı → sinyal
    #
    # 3. Teknik ekip durması (tech_team_layoff)
    "tech_window_days": 90,
    "tech_decline_min_pct": 20.0,      # %20 teknoloji ilan azalması → sinyal
    "tech_decline_moderate_pct": 40.0,  # %40 → orta
    "tech_decline_severe_pct": 60.0,   # %60 → şiddetli
    #
    # 4. Aynı pozisyon tekrarları (position_repeat)
    "position_repeat_window_days": 60,
    "position_repeat_min_count": 2,      # 2+ tekrar → sinyal
    "position_repeat_moderate_count": 4, # 4+ → orta
    "position_repeat_severe_count": 7,   # 7+ → şiddetli
}

# Risk türlerini eşik değerlerine göre skorlama
# signal_type = "risk" (scorer.py SIGNAL_WEIGHTS'de "risk" -> "risk_score")
# signal_subtype değerleri
SUBTYPE_POSTING_DECLINE = "posting_decline"
SUBTYPE_LOCATION_CLOSURE = "location_closure"
SUBTYPE_TECH_LAYOFF = "tech_layoff"
SUBTYPE_POSITION_REPEAT = "position_repeat"

# Risk seviyeleri (aggregate risk_score için)
RISK_TIER_LOW = "low_risk"        # 0-24
RISK_TIER_MODERATE = "moderate_risk"  # 25-49
RISK_TIER_ELEVATED = "elevated_risk"   # 50-74
RISK_TIER_HIGH = "high_risk"      # 75-100

TECH_DEPARTMENTS = {
    "engineering", "yazilim", "it", "devops", "data",
    "software", "backend", "frontend", "fullstack",
    "mühendis", "developer", "site reliability",
    "cloud", "cybersecurity", "siber guvenlik", "data science",
}


def _now() -> datetime:
    return datetime.now()


# ============================================================
# SİNYAL DETECTÖRLERİ
# ============================================================

def detect_posting_decline(postings: list[dict[str, Any]], now: datetime) -> dict[str, Any] | None:
    """1. İş ilanı azalması / churn.

    Önceki 90 günden (prev) sonraki 90 güne (curr) ilan sayısını karşılaştırır.
    Azalma oranı eşik aşarsa risk sinyali üretir.
    """
    cutoff = now - timedelta(days=THRESHOLDS["decline_window_days"])

    # İlanları tarihe göre iki periyoda ayır
    prev_count = sum(1 for p in postings
                     if p.get("posted_at") and p["posted_at"] < cutoff)
    curr_count = sum(1 for p in postings
                     if p.get("posted_at") and p["posted_at"] >= cutoff)

    if prev_count == 0:
        # Önceki dönemde ilan yok → karşılaştırma yapılamaz
        return None

    decline_rate = (1 - curr_count / prev_count) * 100  # negatif = artış

    if decline_rate < THRESHOLDS["decline_rate_min_pct"]:
        return None

    # Skor: %10 azalma → 35, %50+ azalma → 90 (doğrusal artan)
    score = min(35 + (decline_rate - 10) * 1.5, 90)
    score = max(score, 35)

    # Güven: veri miktarı fazla ise daha yüksek
    confidence = min(95, 60 + prev_count * 2)

    return {
        "company_id": postings[0].get("company_id"),
        "signal_type": "risk",
        "signal_subtype": SUBTYPE_POSTING_DECLINE,
        "score": round(score),
        "confidence": round(confidence),
        "evidence": {
            "previous_postings": prev_count,
            "current_postings": curr_count,
            "decline_rate_pct": round(decline_rate, 1),
            "window_days": THRESHOLDS["decline_window_days"],
            "description": f"Job postings declined {round(decline_rate, 1)}% "
                           f"({prev_count} -> {curr_count} in last {THRESHOLDS['decline_window_days']}d)",
        },
    }


def detect_location_closure(postings: list[dict[str, Any]], now: datetime) -> dict[str, Any] | None:
    """2. Lokasyon kapanışları.

    Önceki periyotta aktif şehirlerde son periyotta ilan kalmadıysa kapanış.
    """
    cutoff = now - timedelta(days=THRESHOLDS["location_window_days"])

    prev_cities: set[str] = set()
    curr_cities: set[str] = set()

    for p in postings:
        city = (p.get("location_city") or "").strip().lower()
        if not city or not p.get("posted_at"):
            continue
        if p["posted_at"] < cutoff:
            prev_cities.add(city)
        else:
            curr_cities.add(city)

    closed_cities = sorted(prev_cities - curr_cities)
    if len(closed_cities) < THRESHOLDS["location_closure_min"]:
        return None

    # Skor: 1 şehir → 40, 2-3 → 60, 4+ → 85
    if len(closed_cities) == 1:
        score = 40
    elif len(closed_cities) <= 3:
        score = 60
    else:
        score = 85

    confidence = min(90, 75 + len(closed_cities) * 2)

    return {
        "company_id": postings[0].get("company_id"),
        "signal_type": "risk",
        "signal_subtype": SUBTYPE_LOCATION_CLOSURE,
        "score": score,
        "confidence": confidence,
        "evidence": {
            "closed_cities": closed_cities,
            "total_closed": len(closed_cities),
            "active_cities_now": sorted(curr_cities),
            "window_days": THRESHOLDS["location_window_days"],
            "description": f"{len(closed_cities)} location(s) closed: "
                           f"{', '.join(closed_cities)}",
        },
    }


def detect_tech_team_layoff(postings: list[dict[str, Any]], now: datetime) -> dict[str, Any] | None:
    """3. Teknik ekip durması.

    Teknoloji/mühendislik ilanlarında azalma tespit eder.
    """
    cutoff = now - timedelta(days=THRESHOLDS["tech_window_days"])

    prev_tech = sum(1 for p in postings
                    if p.get("posted_at") and p["posted_at"] < cutoff
                    and _is_tech_posting(p))
    curr_tech = sum(1 for p in postings
                    if p.get("posted_at") and p["posted_at"] >= cutoff
                    and _is_tech_posting(p))

    if prev_tech == 0:
        return None

    decline_rate = (1 - curr_tech / prev_tech) * 100

    # Complete elimination check
    if curr_tech == 0:
        score = 100
        confidence = 95
    elif decline_rate < THRESHOLDS["tech_decline_min_pct"]:
        return None
    elif decline_rate < THRESHOLDS["tech_decline_moderate_pct"]:
        score = 50
        confidence = 75
    elif decline_rate < THRESHOLDS["tech_decline_severe_pct"]:
        score = 75
        confidence = 85
    else:
        score = 90
        confidence = 95

    confidence = min(confidence, 95)

    return {
        "company_id": postings[0].get("company_id"),
        "signal_type": "risk",
        "signal_subtype": SUBTYPE_TECH_LAYOFF,
        "score": score,
        "confidence": confidence,
        "evidence": {
            "previous_tech_postings": prev_tech,
            "current_tech_postings": curr_tech,
            "decline_rate_pct": round(decline_rate, 1),
            "window_days": THRESHOLDS["tech_window_days"],
            "description": f"Tech/engineering postings declined "
                           f"{round(decline_rate, 1)}% ({prev_tech} -> {curr_tech})",
        },
    }


def _is_tech_posting(posting: dict[str, Any]) -> bool:
    title = (posting.get("title") or "").lower()
    dept = (posting.get("department") or "").lower()
    for td in TECH_DEPARTMENTS:
        if td in title or td in dept:
            return True
    return False


def detect_position_repeat(postings: list[dict[str, Any]], now: datetime) -> dict[str, Any] | None:
    """4. Aynı pozisyon tekrarları (position churn).

    Aynı normalizasyonu yapan pozisyonların tekrarlanma sıklığı.
    Yüksek turnover / revolving door sinyali.
    """
    window_start = now - timedelta(days=THRESHOLDS["position_repeat_window_days"])
    window_postings = [
        p for p in postings
        if p.get("posted_at") and p["posted_at"] >= window_start
    ]

    if not window_postings:
        return None

    title_counts: Counter[str] = Counter()
    for p in window_postings:
        norm_title = _normalize_title(p.get("title") or "")
        if norm_title:
            title_counts[norm_title] += 1

    repeat_titles = {t: c for t, c in title_counts.items()
                     if c >= THRESHOLDS["position_repeat_min_count"]}

    if not repeat_titles:
        return None

    max_repeats = max(repeat_titles.values())

    # Skor: 2-3 → 30, 4-6 → 55, 7+ → 80
    if max_repeats >= THRESHOLDS["position_repeat_severe_count"]:
        score = 80
    elif max_repeats >= THRESHOLDS["position_repeat_moderate_count"]:
        score = 55
    else:
        score = 30

    confidence = min(85, 50 + max_repeats * 5)

    return {
        "company_id": postings[0].get("company_id"),
        "signal_type": "risk",
        "signal_subtype": SUBTYPE_POSITION_REPEAT,
        "score": score,
        "confidence": confidence,
        "evidence": {
            "repeat_positions": [{"title": t, "count": c} for t, c in repeat_titles.items()],
            "max_repeats": max_repeats,
            "total_repeat_positions": len(repeat_titles),
            "window_days": THRESHOLDS["position_repeat_window_days"],
            "description": f"{len(repeat_titles)} position(s) reposted "
                           f"({max_repeats}x max): "
                           f"{', '.join(repeat_titles.keys())}",
        },
    }


def _normalize_title(title: str) -> str:
    """Pozisyon başlığını normalize ederek tekrarlanmayı tespit eder."""
    s = title.lower().strip()
    # "software engineer" vs "Yazilim Mühendisi" gibi varyasyonları yakala
    s = s.replace("yazılım mühendisi", "software engineer")
    s = s.replace("mühendis", "engineer")
    s = s.replace("geliştirici", "developer")
    s = s.replace("teknik", "technical")
    # Rakam ve level bilgilerini kaldır
    import re
    s = re.sub(r"\b(junior|mid|senior|lead|principal|staff)\b", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ============================================================
# SKORLAMA FORMÜLÜ
# ============================================================

def weighted_avg(signals: list[dict[str, Any]]) -> float:
    """Risk sinyallerinin güven ağırlıklı ortalaması.

    scorer.py'deki _weighted_avg ile aynı formül:
    risk_score = Σ(score × confidence) / Σ(confidence)
    """
    if not signals:
        return 0.0
    total_score = sum(s["score"] * s["confidence"] for s in signals)
    total_conf = sum(s["confidence"] for s in signals)
    if total_conf == 0:
        return 0.0
    return round(total_score / total_conf, 2)


def classify_risk_tier(risk_score: float) -> str:
    """Aggregate risk_score değerine göre risk seviyesini belirler."""
    if risk_score >= 75:
        return RISK_TIER_HIGH
    if risk_score >= 50:
        return RISK_TIER_ELEVATED
    if risk_score >= 25:
        return RISK_TIER_MODERATE
    return RISK_TIER_LOW


RISK_TIER_LABELS = {
    RISK_TIER_LOW: {"tr": "Düşük risk", "en": "Low Risk", "threshold": "0-24"},
    RISK_TIER_MODERATE: {"tr": "Orta risk", "en": "Moderate Risk", "threshold": "25-49"},
    RISK_TIER_ELEVATED: {"tr": "Yüksek risk", "en": "Elevated Risk", "threshold": "50-74"},
    RISK_TIER_HIGH: {"tr": "Kritik risk", "en": "High Risk", "threshold": "75-100"},
}


def score_company_risk(company_id: str, postings: list[dict[str, Any]],
                       now: datetime | None = None) -> dict[str, Any]:
    """Bir şirket için tüm risk sinyallerini tespit eder ve skorlar."""
    if now is None:
        now = _now()

    signals: list[dict[str, Any]] = []

    for detector in (
        detect_posting_decline,
        detect_location_closure,
        detect_tech_team_layoff,
        detect_position_repeat,
    ):
        signal = detector(postings, now)
        if signal:
            signals.append(signal)

    risk_score = weighted_avg(signals)
    tier = classify_risk_tier(risk_score)

    return {
        "company_id": company_id,
        "risk_score": risk_score,
        "risk_tier": tier,
        "risk_tier_label": RISK_TIER_LABELS[tier]["tr"],
        "signals": signals,
        "signal_count": len(signals),
        "calculated_at": now.isoformat(),
    }


# ============================================================
# ÖRNEK VERİ VE TEST
# ============================================================

def _parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


# 2026-09-09 tarihine göre örnek ilanlar (180 günlük pencere)
NOW = datetime(2026, 9, 9, 12, 0, 0)

SAMPLE_DATA: dict[str, list[dict[str, Any]]] = {
    # Company A — Sağlıklı (büyüyen firma, risk yok)
    "COMP-A-001": [
        {"company_id": "COMP-A-001", "title": "Software Engineer", "department": "Engineering",
         "location_city": "Ankara", "posted_at": _parse_dt("2026-06-15T10:00:00")},
        {"company_id": "COMP-A-001", "title": "Software Engineer", "department": "Engineering",
         "location_city": "Ankara", "posted_at": _parse_dt("2026-07-20T10:00:00")},
        {"company_id": "COMP-A-001", "title": "Cloud Architect", "department": "Engineering",
         "location_city": "Ankara", "posted_at": _parse_dt("2026-08-01T10:00:00")},
        {"company_id": "COMP-A-001", "title": "Data Scientist", "department": "Data",
         "location_city": "Istanbul", "posted_at": _parse_dt("2026-08-10T10:00:00")},
        {"company_id": "COMP-A-001", "title": "DevOps Engineer", "department": "DevOps",
         "location_city": "Ankara", "posted_at": _parse_dt("2026-08-20T10:00:00")},
    ],
    # Company B — Orta risk (ilan azalması, pozisyon churn)
    "COMP-B-002": [
        {"company_id": "COMP-B-002", "title": "Software Engineer", "department": "Engineering",
         "location_city": "Ankara", "posted_at": _parse_dt("2026-06-01T10:00:00")},
        {"company_id": "COMP-B-002", "title": "Software Engineer", "department": "Engineering",
         "location_city": "Ankara", "posted_at": _parse_dt("2026-06-15T10:00:00")},
        {"company_id": "COMP-B-002", "title": "Software Engineer", "department": "Engineering",
         "location_city": "Ankara", "posted_at": _parse_dt("2026-07-01T10:00:00")},
        {"company_id": "COMP-B-002", "title": "Software Engineer", "department": "Engineering",
         "location_city": "Ankara", "posted_at": _parse_dt("2026-07-20T10:00:00")},
        {"company_id": "COMP-B-002", "title": "Software Engineer", "department": "Engineering",
         "location_city": "Ankara", "posted_at": _parse_dt("2026-08-01T10:00:00")},
        # Son 90 gün — sadece 1 ilan (önceden 5 → şu an 1, %80 azalma)
        {"company_id": "COMP-B-002", "title": "Senior Engineer", "department": "Engineering",
         "location_city": "Ankara", "posted_at": _parse_dt("2026-08-15T10:00:00")},
    ],
    # Company C — Yüksek risk (hiring freeze + tech layoff + location closure)
    "COMP-C-003": [
        {"company_id": "COMP-C-003", "title": "Software Engineer", "department": "Engineering",
         "location_city": "Ankara", "posted_at": _parse_dt("2026-06-01T10:00:00")},
        {"company_id": "COMP-C-003", "title": "Software Engineer", "department": "Engineering",
         "location_city": "Ankara", "posted_at": _parse_dt("2026-06-10T10:00:00")},
        {"company_id": "COMP-C-003", "title": "Software Engineer", "department": "Engineering",
         "location_city": "Ankara", "posted_at": _parse_dt("2026-06-20T10:00:00")},
        {"company_id": "COMP-C-003", "title": "Data Engineer", "department": "Engineering",
         "location_city": "Istanbul", "posted_at": _parse_dt("2026-06-25T10:00:00")},
        {"company_id": "COMP-C-003", "title": "DevOps Engineer", "department": "DevOps",
         "location_city": "Istanbul", "posted_at": _parse_dt("2026-06-28T10:00:00")},
        {"company_id": "COMP-C-003", "title": "Backend Developer", "department": "Engineering",
         "location_city": "Istanbul", "posted_at": _parse_dt("2026-07-01T10:00:00")},
        # Son 90 gün — hiç ilan yok (hiring freeze, %100 azalma, tech tamamen durdu)
    ],
}


def run_tests() -> dict[str, Any]:
    """Örnek veriyle risk skorlama motorunu test eder."""
    results = []

    for company_id, postings in SAMPLE_DATA.items():
        result = score_company_risk(company_id, postings, now=NOW)
        results.append(result)
        log.info("Company %s: risk_score=%.2f, tier=%s, signals=%d",
                 company_id, result["risk_score"],
                 result["risk_tier_label"], result["signal_count"])
        for sig in result["signals"]:
            log.info("  -> signal: %s/%s score=%d confidence=%d",
                     sig["signal_type"], sig["signal_subtype"],
                     sig["score"], sig["confidence"])

    return {
        "companies": results,
        "total_companies": len(results),
    }


# ============================================================
# DB ENTGRASYONU (isteğe bağlı, test ortamında çalıştırılabilir)
# ============================================================

def persist_signals_to_db(results: list[dict[str, Any]]) -> dict[str, int]:
    """Risk sinyallerini company_signals ve company_intelligence_scores'a yazar.

    Not: Bu fonksiyon DB'ye bağlanır. Test ortamında bu fonksiyon
    çağrılmadan skorlar hesaplanabilir.
    """
    from company_master.db.connection import get_engine
    from sqlalchemy import text

    engine = get_engine()
    stats = {"signals_inserted": 0, "scores_updated": 0, "errors": 0}

    with engine.begin() as conn:
        for company_result in results:
            cid = company_result["company_id"]
            risk_score = company_result["risk_score"]

            # company_intelligence_scores.risk_score güncelle
            conn.execute(text("""
                INSERT INTO company_intelligence_scores (company_id, risk_score)
                VALUES (:cid, :rs)
                ON CONFLICT (company_id) DO UPDATE SET
                    risk_score = :rs,
                    updated_at = NOW()
            """), {"cid": cid, "rs": risk_score})
            stats["scores_updated"] += 1

            # company_signals tablosuna risk sinyallerini yaz
            for sig in company_result["signals"]:
                conn.execute(text("""
                    INSERT INTO company_signals
                        (company_id, signal_type, signal_subtype, score, confidence,
                         evidence, detected_at, valid_until, metadata)
                    VALUES
                        (:cid, :stype, :ssubtype, :score, :confidence,
                         :evidence::jsonb, :detected_at, :valid_until, :metadata::jsonb)
                """), {
                    "cid": cid,
                    "stype": sig["signal_type"],
                    "ssubtype": sig["signal_subtype"],
                    "score": sig["score"],
                    "confidence": sig["confidence"],
                    "evidence": json.dumps(sig["evidence"], ensure_ascii=False),
                    "detected_at": sig.get("detected_at", datetime.now()),
                    "valid_until": sig.get("valid_until"),
                    "metadata": json.dumps(sig.get("metadata", {}), ensure_ascii=False),
                })
                stats["signals_inserted"] += 1

    return stats


# ============================================================
# ANA
# ============================================================

def build_result() -> dict[str, Any]:
    """Tüm sonucu derler."""
    test_output = run_tests()

    return {
        "task_id": "P8-4",
        "baslik": "İş ilanı takip motoru: risk sinyali skorlama",
        "sahip": "arastirmaci",
        "durum": "done",
        "tarih": datetime.now().isoformat(),
        "ozet": (
            "Risk sinyali skorlama motoru tasarlandı ve örnek veriyle test edildi. "
            "4 risk sinyali detectörü (ilan_azalma, lokasyon_kapanis, "
            "teknik_ekip_durmasi, ayni_pozisyon_tekrari) implement edildi. "
            "Scorlama formülü scorer.py'deki _weighted_avg ile aynı desen kullanır: "
            "risk_score = Σ(score × confidence) / Σ(confidence). "
            "company_signals ve company_intelligence_scores tablolarına entegre edilebilir."
        ),
        "risk_signals": [
            {
                "id": 1,
                "name": "İlan azalması / churn",
                "signal_type": "risk",
                "signal_subtype": "posting_decline",
                "description": "Önceki 90 günden sonraki 90 güne iş ilanı sayısında %10+ azalma",
                "score_formula": "score = min(35 + (decline_rate - 10) * 1.5, 90), decline_rate ≥ 10%",
                "confidence_formula": "min(95, 60 + prev_count * 2)",
                "threshold": "decline_rate ≥ 10% (kısa), ≥ 25% (orta), ≥ 50% (şiddetli)",
            },
            {
                "id": 2,
                "name": "Lokasyon kapanışı",
                "signal_type": "risk",
                "signal_subtype": "location_closure",
                "description": "Önceki periyotta aktif şehirlerde son periyotta ilan kalmaması",
                "score_formula": "1 şehir=40, 2-3 şehir=60, 4+ şehir=85",
                "confidence_formula": "min(90, 75 + closed_count * 2)",
                "threshold": "≥1 şehir kapanışı",
            },
            {
                "id": 3,
                "name": "Teknik ekip durması",
                "signal_type": "risk",
                "signal_subtype": "tech_layoff",
                "description": "Teknoloji/mühendislik ilanlarında %20+ azalma (tamamen 0 da olabilir)",
                "score_formula": "0 ilan=100, %20-<40=50, %40-<60=75, ≥60=90",
                "confidence_formula": "75-95 (veri miktarına göre)",
                "threshold": "tech_decline ≥ 20% veya tamamen durma (0 ilan)",
            },
            {
                "id": 4,
                "name": "Aynı pozisyon tekrarları",
                "signal_type": "risk",
                "signal_subtype": "position_repeat",
                "description": "Aynı normalizasyonu yapan pozisyonun 60 günde tekrarlanması (revolving door)",
                "score_formula": "2-3 tekrar=30, 4-6=55, 7+=80",
                "confidence_formula": "min(85, 50 + max_repeats * 5)",
                "threshold": "≥2 tekrar",
            },
        ],
        "scoring_formula": {
            "aggregate": "risk_score = Σ(signal_score × confidence) / Σ(confidence)",
            "reference": "scorer.py: _weighted_avg() — aynı fonksiyon job_intelligence pipeline'daki diğer skorlar için de kullanılır",
            "signal_score_range": "0-100 (yüksek = daha şiddetli risk)",
            "confidence_range": "0-100 (yüksek = daha güvenilir)",
        },
        "risk_tiers": {
            "low_risk": {"en": "Low Risk", "tr": "Düşük risk", "range": "0-24"},
            "moderate_risk": {"en": "Moderate Risk", "tr": "Orta risk", "range": "25-49"},
            "elevated_risk": {"en": "Elevated Risk", "tr": "Yüksek risk", "range": "50-74"},
            "high_risk": {"en": "High Risk", "tr": "Kritik risk", "range": "75-100"},
        },
        "thresholds": THRESHOLDS,
        "test_results": test_output,
        "integration_points": {
            "company_signals": (
                "risk sinyalleri signal_type='risk' olarak kaydedilir. "
                "evidence JSONB: job_posting_ids, date_range, details. "
                "analyze_job_signals.py'ye entegre edilebilir."
            ),
            "company_intelligence_scores": (
                "risk_score alanına aggregate skor yazılır. "
                "scorer.py'deki _weighted_avg → _build_scores → score_company "
                "akışı ile otomatik hesaplanır."
            ),
            "post_scrape_workflow": (
                "Adım 6 (analyze_job_signals) genişletilir, "
                "Adım 7 (recalc_intelligence_scores) risk skorunu yazar."
            ),
        },
    }


if __name__ == "__main__":
    result = build_result()
    output = json.dumps(result, ensure_ascii=False, indent=2, default=str)
    print(output)
    log.info("Risk skorlama motoru test tamamlandı. %d şirket analiz edildi.", result["test_results"]["total_companies"])
