# -*- coding: utf-8 -*-
"""Job Intelligence — Intelligence Scorer."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import text

from company_master.db.connection import get_engine

logger = logging.getLogger(__name__)

SIGNAL_WEIGHTS: dict[str, str] = {
    "growth": "growth_score",
    "geo_expansion": "expansion_score",
    "tech_transformation": "tech_transformation_score",
    "investment": "investment_signal_score",
    "org_change": "org_change_score",
    "risk": "risk_score",
}

CRITICAL_SENIORITIES = {"director", "c-level", "vp", "head", "manager"}

def _now() -> datetime:
    return datetime.utcnow()

def _load_active_signals() -> list[dict[str, Any]]:
    engine = get_engine()
    query = text("""
        SELECT signal_id, company_id, signal_type, signal_subtype,
               score, confidence, evidence, detected_at, valid_until, metadata
        FROM company_signals
        WHERE valid_until IS NULL OR valid_until > NOW()
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()
    return [dict(r) for r in rows]

def _group_by_company(signals: list[dict[str, Any]]) -> dict[UUID, list[dict[str, Any]]]:
    grouped: dict[UUID, list[dict[str, Any]]] = {}
    for s in signals:
        cid = s["company_id"]
        grouped.setdefault(cid, []).append(s)
    return grouped

def _weighted_avg(signals: list[dict[str, Any]]) -> float:
    if not signals:
        return 0.0
    total_score = sum(s["score"] * s["confidence"] for s in signals)
    total_conf = sum(s["confidence"] for s in signals)
    if total_conf == 0:
        return 0.0
    return round(total_score / total_conf, 2)

def _compute_signal_counts(signals: list[dict[str, Any]]) -> tuple[int, int]:
    now = _now()
    count_30d = sum(1 for s in signals if (now - s["detected_at"]).days <= 30)
    count_90d = sum(1 for s in signals if (now - s["detected_at"]).days <= 90)
    return count_30d, count_90d

def _determine_hiring_trend(count_30d: int, count_90d: int) -> str:
    if count_90d == 0:
        return "unknown" if count_30d == 0 else "accelerating"
    ratio = count_30d / count_90d
    if ratio >= 1.5:
        return "accelerating"
    if ratio <= 0.5:
        return "decelerating"
    return "stable"

def _extract_new_locations(signals: list[dict[str, Any]]) -> list[str]:
    locations: set[str] = set()
    for s in signals:
        if s["signal_type"] != "geo_expansion":
            continue
        evidence = s.get("evidence") or {}
        city = evidence.get("city") or evidence.get("location_city")
        if city:
            locations.add(str(city))
    return sorted(locations)

def _extract_new_departments(signals: list[dict[str, Any]]) -> list[str]:
    departments: set[str] = set()
    for s in signals:
        if s["signal_type"] != "org_change":
            continue
        evidence = s.get("evidence") or {}
        dept = evidence.get("department") or evidence.get("new_department")
        if dept:
            departments.add(str(dept))
    return sorted(departments)

def _extract_critical_hires(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hires: list[dict[str, Any]] = []
    for s in signals:
        if s["signal_type"] not in ("growth", "investment"):
            continue
        evidence = s.get("evidence") or {}
        seniority = str(evidence.get("seniority_level", "")).lower()
        if seniority in CRITICAL_SENIORITIES:
            hires.append({
                "signal_id": str(s["signal_id"]),
                "company_id": str(s["company_id"]),
                "title": evidence.get("title", ""),
                "seniority_level": seniority,
                "department": evidence.get("department", ""),
                "location": evidence.get("city") or evidence.get("location_city", ""),
                "detected_at": s["detected_at"].isoformat() if hasattr(s["detected_at"], "isoformat") else str(s["detected_at"]),
            })
    return hires

def _build_detected_signals(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for s in signals:
        result.append({
            "signal_id": str(s["signal_id"]),
            "company_id": str(s["company_id"]),
            "signal_type": s["signal_type"],
            "signal_subtype": s["signal_subtype"],
            "score": s["score"],
            "confidence": s["confidence"],
            "evidence": s["evidence"],
            "detected_at": s["detected_at"].isoformat() if hasattr(s["detected_at"], "isoformat") else str(s["detected_at"]),
            "metadata": s["metadata"],
        })
    return result

def _compute_overall_confidence(signals: list[dict[str, Any]]) -> float:
    if not signals:
        return 0.0
    total = sum(s["confidence"] for s in signals)
    return round(total / len(signals), 2)

def _build_scores(company_id: UUID, signals: list[dict[str, Any]]) -> dict[str, Any]:
    by_type: dict[str, list[dict[str, Any]]] = {}
    for s in signals:
        by_type.setdefault(s["signal_type"], []).append(s)

    score_fields = {}
    for stype, field in SIGNAL_WEIGHTS.items():
        score_fields[field] = _weighted_avg(by_type.get(stype, []))

    count_30d, count_90d = _compute_signal_counts(signals)
    hiring_trend = _determine_hiring_trend(count_30d, count_90d)
    new_locations = _extract_new_locations(signals)
    new_departments = _extract_new_departments(signals)
    critical_hires = _extract_critical_hires(signals)
    detected_signals = _build_detected_signals(signals)
    overall_confidence = _compute_overall_confidence(signals)

    now = _now()
    return {
        "company_id": company_id,
        **score_fields,
        "hiring_trend": hiring_trend,
        "new_locations": new_locations,
        "new_departments": new_departments,
        "critical_hires": critical_hires,
        "detected_signals": detected_signals,
        "signal_count_30d": count_30d,
        "signal_count_90d": count_90d,
        "overall_confidence": overall_confidence,
        "last_calculated_at": now,
        "updated_at": now,
    }

def score_company(company_id: UUID, signals: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not signals:
        return None
    scores = _build_scores(company_id, signals)
    engine = get_engine()
    columns = list(scores.keys())
    placeholders = ", ".join(f"{c} = :{c}" for c in columns)
    col_str = ", ".join(columns)
    query = text(f"""
        INSERT INTO company_intelligence_scores ({col_str})
        VALUES ({placeholders})
        ON CONFLICT (company_id) DO UPDATE SET {placeholders}
    """)
    with engine.connect() as conn:
        conn.execute(query, scores)
        conn.commit()
    logger.info("Scored company %s: %d signals, confidence=%.2f", company_id, len(signals), scores["overall_confidence"])
    return scores

def score_all_companies() -> dict[str, Any]:
    signals = _load_active_signals()
    grouped = _group_by_company(signals)
    results: dict[str, Any] = {"processed": 0, "skipped": 0, "companies": []}
    for company_id, comp_signals in grouped.items():
        if not comp_signals:
            results["skipped"] += 1
            continue
        try:
            scores = score_company(company_id, comp_signals)
            if scores:
                results["processed"] += 1
                results["companies"].append(str(company_id))
        except Exception:
            logger.exception("Failed to score company %s", company_id)
            results["skipped"] += 1
    logger.info("score_all_companies done: %d processed, %d skipped", results["processed"], results["skipped"])
    return results

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger.info("Starting Job Intelligence Scorer")
    result = score_all_companies()
    logger.info("Scorer complete: %d companies processed", result["processed"])

if __name__ == "__main__":
    main()
