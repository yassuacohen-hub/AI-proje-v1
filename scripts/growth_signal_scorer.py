# -*- coding: utf-8 -*-
"""Growth Signal Scoring Engine for P8-3.

Is ilanlarindan buyume sinyalleri tespit eder, skorlar ve
company_intelligence_scores.growth_score alanini doldurur.

Bes sinyal:
  1. Hiring surge (growth, weight 0.30)     - ilan artis hizi (aylik %)
  2. New location (geo_expansion, weight 0.15) - yeni sehir acilisi
  3. New department (org_change, weight 0.10) - yeni departman
  4. Executive hire (investment, weight 0.25) - yonetici ise alimi
  5. Sales expansion (tech_transformation, weight 0.20) - satis ekip genislesmesi

Formula:
    growth_score = sum(sub_score_i * confidence_i * weight_i) /
                   sum(confidence_i * weight_i)
    clamped to [0, 100]. Negatif hiring trend decay faktoru uygular.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

# --- Scoring weights — from project.md (job_intelligence_scoring_weights) ---
SIGNAL_WEIGHTS: dict[str, float] = {
    "growth": 0.30,
    "investment": 0.25,
    "tech_transformation": 0.20,
    "geo_expansion": 0.15,
    "org_change": 0.10,
}

EXECUTIVE_LEVELS = {"director", "c-level", "vp", "head", "manager", "lead"}
SALES_DEPT_KEYWORDS = {"sales", "business development", "account management",
                        "revenue", "bd", "channel", "partner"}
SALES_TITLE_KEYWORDS = {"sales", "business development", "account manager",
                         "revenue", "bd", "channel", "partner", "sales engineer"}

# --- Threshold definitions for each signal subtype ---
_THRESHOLDS: dict[str, Any] = {
    "hiring_surge": {
        ">=50pct_increase": {"min_growth_rate": 50, "score": 100},
        "20-49pct_increase": {"min_growth_rate": 20, "score": 80},
        "10-19pct_increase": {"min_growth_rate": 10, "score": 60},
        "0-9pct_increase": {"min_growth_rate": 0, "score": 40},
        "<0pct_decline": {
            "max_growth_rate": 0,
            "score_formula": "40 * (1 + rate/100), clamped [0, 39]",
        },
    },
    "new_location": {
        "3+_new_cities": {"min_count": 3, "score": 100},
        "2_new_cities": {"min_count": 2, "score": 90},
        "1_new_city": {"min_count": 1, "score": 80},
    },
    "new_department": {
        "3+_new_departments": {"min_count": 3, "score": 100},
        "2_new_departments": {"min_count": 2, "score": 90},
        "1_new_department": {"min_count": 1, "score": 80},
    },
    "executive_hire": {
        "3+_executive_hires": {"min_count": 3, "score": 100},
        "2_executive_hires": {"min_count": 2, "score": 85},
        "1_executive_hire": {"min_count": 1, "score": 60},
    },
    "sales_expansion": {
        "6+_sales_hires": {"min_count": 6, "score": 100},
        "3-5_sales_hires": {"min_count": 3, "score": 75},
        "1-2_sales_hires": {"min_count": 1, "score": 50},
    },
}


@dataclass
class SignalResult:
    """Son single growth signal detection result."""

    signal_type: str
    signal_subtype: str
    score: float = 0.0
    confidence: float = 0.0
    evidence: dict[str, Any] = field(default_factory=dict)
    threshold_breached: str | None = None


def _month_key(dt: datetime) -> str:
    """Return YYYY-MM string for a datetime."""
    return dt.strftime("%Y-%m")


def _detect_hiring_surge(
    postings: list[dict[str, Any]],
    current_month: str,
    previous_month: str,
) -> SignalResult:
    """Detect job posting increase rate (aylik %). Growth weight: 0.30."""
    current_count = sum(
        1 for p in postings if _month_key(p["posted_at"]) == current_month
    )
    previous_count = sum(
        1 for p in postings if _month_key(p["posted_at"]) == previous_month
    )

    if previous_count == 0:
        if current_count > 0:
            growth_rate = 100.0
            threshold = "first_hiring"
        else:
            growth_rate = 0.0
            threshold = "no_postings"
    else:
        growth_rate = ((current_count - previous_count) / previous_count) * 100
        if growth_rate >= 50:
            threshold = ">=50pct_increase"
        elif growth_rate >= 20:
            threshold = "20-49pct_increase"
        elif growth_rate >= 10:
            threshold = "10-19pct_increase"
        elif growth_rate >= 0:
            threshold = "0-9pct_increase"
        else:
            threshold = "<0pct_decline"

    if growth_rate >= 50:
        score = 100.0
    elif growth_rate >= 20:
        score = 80.0
    elif growth_rate >= 10:
        score = 60.0
    elif growth_rate >= 0:
        score = 40.0
    else:
        score = max(0.0, 40.0 * (1.0 + growth_rate / 100.0))

    confidence = min(100.0, max(10.0, current_count * 10.0))
    if previous_count == 0 and current_count > 0:
        confidence = min(100.0, current_count * 20.0)

    return SignalResult(
        signal_type="growth",
        signal_subtype="hiring_surge",
        score=round(score, 2),
        confidence=round(confidence, 2),
        evidence={
            "current_month": current_month,
            "previous_month": previous_month,
            "current_posting_count": current_count,
            "previous_posting_count": previous_count,
            "growth_rate_pct": round(growth_rate, 2),
        },
        threshold_breached=threshold,
    )


def _detect_new_location(
    postings: list[dict[str, Any]],
    current_month: str,
    historical_cities: set[str],
) -> SignalResult:
    """Detect new city/location hiring. Geo expansion weight: 0.15."""
    current_cities = {
        p["location_city"]
        for p in postings
        if _month_key(p["posted_at"]) == current_month
        and p.get("location_city")
    }
    new_cities = current_cities - historical_cities

    if not new_cities:
        score, threshold = 0.0, "no_new_locations"
    elif len(new_cities) >= 3:
        score, threshold = 100.0, "3+_new_cities"
    elif len(new_cities) == 2:
        score, threshold = 90.0, "2_new_cities"
    else:
        score, threshold = 80.0, "1_new_city"

    current_postings_in_new = sum(
        1
        for p in postings
        if _month_key(p["posted_at"]) == current_month
        and p.get("location_city") in new_cities
    )
    confidence = 100.0 if current_postings_in_new >= 2 else 70.0

    return SignalResult(
        signal_type="geo_expansion",
        signal_subtype="new_location",
        score=round(score, 2),
        confidence=round(confidence, 2),
        evidence={
            "new_cities": sorted(new_cities),
            "new_location_count": len(new_cities),
            "postings_in_new_locations": current_postings_in_new,
            "historical_cities": sorted(historical_cities),
        },
        threshold_breached=threshold,
    )


def _detect_new_department(
    postings: list[dict[str, Any]],
    current_month: str,
    historical_departments: set[str],
) -> SignalResult:
    """Detect new department hiring. Org change weight: 0.10."""
    current_depts = {
        p.get("department")
        for p in postings
        if _month_key(p["posted_at"]) == current_month
        and p.get("department")
    }
    new_depts = current_depts - historical_departments

    if not new_depts:
        score, threshold = 0.0, "no_new_departments"
    elif len(new_depts) >= 3:
        score, threshold = 100.0, "3+_new_departments"
    elif len(new_depts) == 2:
        score, threshold = 90.0, "2_new_departments"
    else:
        score, threshold = 80.0, "1_new_department"

    confidence = min(100.0, len(new_depts) * 40.0 + 20.0)

    return SignalResult(
        signal_type="org_change",
        signal_subtype="new_department",
        score=round(score, 2),
        confidence=round(confidence, 2),
        evidence={
            "new_departments": sorted(d for d in new_depts if d),
            "new_department_count": len(new_depts),
            "historical_departments": sorted(d for d in historical_departments if d),
        },
        threshold_breached=threshold,
    )


def _detect_executive_hiring(
    postings: list[dict[str, Any]],
    current_month: str,
) -> SignalResult:
    """Detect executive/leadership hiring (yonetici ise alimi). Investment weight: 0.25."""
    current_postings = [
        p for p in postings if _month_key(p["posted_at"]) == current_month
    ]
    exec_hires = [
        p
        for p in current_postings
        if (p.get("seniority_level") or "").lower() in EXECUTIVE_LEVELS
    ]

    exec_count = len(exec_hires)
    if exec_count >= 3:
        score, threshold = 100.0, "3+_executive_hires"
    elif exec_count == 2:
        score, threshold = 85.0, "2_executive_hires"
    elif exec_count == 1:
        score, threshold = 60.0, "1_executive_hire"
    else:
        score, threshold = 0.0, "no_executive_hires"

    confidence = 100.0
    exec_details = [
        {
            "title": p.get("title", ""),
            "seniority_level": p.get("seniority_level", ""),
            "department": p.get("department", ""),
        }
        for p in exec_hires
    ]

    return SignalResult(
        signal_type="investment",
        signal_subtype="executive_hire",
        score=round(score, 2),
        confidence=round(confidence, 2),
        evidence={
            "executive_hire_count": exec_count,
            "executive_hires": exec_details,
        },
        threshold_breached=threshold,
    )


def _detect_sales_expansion(
    postings: list[dict[str, Any]],
    current_month: str,
) -> SignalResult:
    """Detect sales team expansion (satis ekip genislesmesi). Tech weight: 0.20."""
    current_postings = [
        p for p in postings if _month_key(p["posted_at"]) == current_month
    ]
    sales_hires = []
    for p in current_postings:
        title_lower = (p.get("title") or "").lower()
        dept_lower = (p.get("department") or "").lower()
        if (
            any(kw in title_lower for kw in SALES_TITLE_KEYWORDS)
            or any(kw in dept_lower for kw in SALES_DEPT_KEYWORDS)
        ):
            sales_hires.append(p)

    sales_count = len(sales_hires)
    if sales_count >= 6:
        score, threshold = 100.0, "6+_sales_hires"
    elif 3 <= sales_count <= 5:
        score, threshold = 75.0, "3-5_sales_hires"
    elif 1 <= sales_count <= 2:
        score, threshold = 50.0, "1-2_sales_hires"
    else:
        score, threshold = 0.0, "no_sales_hires"

    confidence = min(100.0, sales_count * 25.0 + 50.0)

    return SignalResult(
        signal_type="tech_transformation",
        signal_subtype="sales_expansion",
        score=round(score, 2),
        confidence=round(confidence, 2),
        evidence={
            "sales_hire_count": sales_count,
            "sales_roles": [
                {
                    "title": p.get("title", ""),
                    "department": p.get("department", ""),
                }
                for p in sales_hires
            ],
        },
        threshold_breached=threshold,
    )


def compute_growth_score(
    postings: list[dict[str, Any]],
    company_id: str | None = None,
    current_month: str | None = None,
    previous_month: str | None = None,
    historical_cities: set[str] | None = None,
    historical_departments: set[str] | None = None,
) -> dict[str, Any]:
    """Compute growth_score (0-100) for a single company from its job_postings.

    Returns dict with: growth_score, hiring_trend, signals, weighted_components,
    formula, weights, thresholds.
    """
    now = datetime.utcnow()
    if current_month is None:
        current_month = _month_key(now)
    if previous_month is None:
        previous_month = _month_key(now - timedelta(days=30))
    if historical_cities is None:
        historical_cities = set()
    if historical_departments is None:
        historical_departments = set()

    signals = [
        _detect_hiring_surge(postings, current_month, previous_month),
        _detect_new_location(postings, current_month, historical_cities),
        _detect_new_department(postings, current_month, historical_departments),
        _detect_executive_hiring(postings, current_month),
        _detect_sales_expansion(postings, current_month),
    ]

    # Weighted average: sum(score * confidence * weight) / sum(confidence * weight)
    numerator = 0.0
    denominator = 0.0
    components = []

    for sig in signals:
        w = SIGNAL_WEIGHTS.get(sig.signal_type, 0.0)
        contrib = sig.score * sig.confidence * w
        weight_conf = sig.confidence * w
        numerator += contrib
        denominator += weight_conf
        components.append({
            "signal_type": sig.signal_type,
            "signal_subtype": sig.signal_subtype,
            "weight": w,
            "score": sig.score,
            "confidence": sig.confidence,
            "contribution": round(contrib, 2),
            "weighted_contribution_pct": round(contrib / max(weight_conf, 0.001), 2),
        })

    raw_growth_score = (
        round(numerator / denominator, 2) if denominator > 0 else 0.0
    )

    # Negative trend handling: if hiring declining, apply decay factor
    surge = signals[0]
    growth_rate = surge.evidence.get("growth_rate_pct", 0.0)
    if growth_rate < 0:
        decayed = raw_growth_score * (1.0 + growth_rate / 100.0)
        final_growth_score = round(max(0.0, min(100.0, decayed)), 2)
        trend_note = (
            f"Negative trend ({growth_rate}%); score decayed via (1 + rate/100)"
        )
    else:
        final_growth_score = raw_growth_score
        trend_note = None

    # Determine hiring trend label
    if growth_rate >= 50:
        hiring_trend = "accelerating"
    elif growth_rate >= 10:
        hiring_trend = "stable"
    elif growth_rate >= -10:
        hiring_trend = "decelerating"
    elif growth_rate < -10:
        hiring_trend = "contracting"
    else:
        hiring_trend = "unknown" if growth_rate == 0 else "decelerating"

    if growth_rate == 0 and surge.evidence.get("current_posting_count", 0) == 0:
        hiring_trend = "unknown"

    result = {
        "company_id": str(company_id) if company_id else None,
        "growth_score": final_growth_score,
        "hiring_trend": hiring_trend,
        "raw_growth_score": raw_growth_score,
        "growth_rate_pct": round(growth_rate, 2),
        "signals": [
            {
                "signal_type": s.signal_type,
                "signal_subtype": s.signal_subtype,
                "score": s.score,
                "confidence": s.confidence,
                "threshold_breached": s.threshold_breached,
                "evidence": s.evidence,
            }
            for s in signals
        ],
        "weighted_components": components,
        "formula": (
            "growth_score = sum(sub_score_i * confidence_i * weight_i) / "
            "sum(confidence_i * weight_i), clamped [0, 100]"
        ),
        "weights": SIGNAL_WEIGHTS,
        "thresholds": _THRESHOLDS,
    }

    if trend_note:
        result["trend_note"] = trend_note

    return result


def _generate_sample_postings() -> list[dict[str, Any]]:
    """Generate sample job_postings data for testing (3 companies)."""
    now = datetime(2026, 9, 9, 12, 0, 0)
    prev_month = datetime(2026, 8, 1, 12, 0, 0)
    postings: list[dict[str, Any]] = []

    # Company A: StarTech Engineering - strong growth across all signals
    # Sep: 15 postings, Aug: 5 postings => 200% increase
    company_a_id = uuid4()
    for i in range(5):
        postings.append({
            "company_id": company_a_id,
            "posted_at": prev_month + timedelta(days=i),
            "title": f"Software Engineer {i+1}",
            "department": "Engineering",
            "seniority_level": "senior",
            "location_city": "Ankara",
        })
    for i in range(15):
        city = ["Ankara", "Istanbul", "Izmir"][i % 3]
        dept = ["Engineering", "Sales", "HR"][i % 3]
        seniority = ["senior", "director", "manager", "c-level"][i % 4] if i < 4 else "junior"
        title = [
            "Software Engineer", "Sales Representative", "HR Specialist",
            "Director of Engineering", "Sales Manager", "CTO",
            "Business Development Manager", "Senior Engineer",
        ][i % 8]
        postings.append({
            "company_id": company_a_id,
            "posted_at": now + timedelta(days=i),
            "title": title,
            "department": dept,
            "seniority_level": seniority,
            "location_city": city,
        })

    # Company B: SteadyCo - moderate growth
    # Sep: 10 postings, Aug: 8 postings => 25% increase
    company_b_id = uuid4()
    for i in range(8):
        postings.append({
            "company_id": company_b_id,
            "posted_at": prev_month + timedelta(days=i * 3),
            "title": f"Engineer {i+1}",
            "department": "Engineering",
            "seniority_level": "mid",
            "location_city": "Ankara",
        })
    for i in range(10):
        dept = ["Engineering", "Sales"][i % 2]
        seniority = "senior" if i < 2 else "junior"
        title = ["Senior Engineer", "Sales Executive"][i % 2]
        postings.append({
            "company_id": company_b_id,
            "posted_at": now + timedelta(days=i),
            "title": title,
            "department": dept,
            "seniority_level": seniority,
            "location_city": "Ankara",
        })

    # Company C: DeclineCorp - contracting (-96% hiring)
    # Aug: 80 postings, Sep: 3 postings => -96.25%
    company_c_id = uuid4()
    for i in range(80):
        postings.append({
            "company_id": company_c_id,
            "posted_at": prev_month + timedelta(days=i % 30),
            "title": f"Engineer {i+1}",
            "department": "Engineering",
            "seniority_level": "junior",
            "location_city": "Ankara",
        })
    for i in range(3):
        postings.append({
            "company_id": company_c_id,
            "posted_at": now + timedelta(days=i),
            "title": f"Engineer {i+1}",
            "department": "Engineering",
            "seniority_level": "junior",
            "location_city": "Ankara",
        })

    return postings


def run_tests() -> dict[str, Any]:
    """Run the growth signal scoring engine with sample data."""
    now = datetime(2026, 9, 9, 12, 0, 0)
    current_month = _month_key(now)
    previous_month = _month_key(now - timedelta(days=30))

    postings = _generate_sample_postings()
    companies: dict[UUID, list[dict[str, Any]]] = {}
    for p in postings:
        cid = p["company_id"]
        companies.setdefault(cid, []).append(p)

    results: list[dict[str, Any]] = []
    for company_id, comp_postings in companies.items():
        hist_cities = {
            p["location_city"]
            for p in comp_postings
            if _month_key(p["posted_at"]) == previous_month
            and p.get("location_city")
        }
        hist_depts = {
            p.get("department")
            for p in comp_postings
            if _month_key(p["posted_at"]) == previous_month
            and p.get("department")
        }
        result = compute_growth_score(
            postings=comp_postings,
            company_id=str(company_id),
            current_month=current_month,
            previous_month=previous_month,
            historical_cities=hist_cities,
            historical_departments=hist_depts,
        )
        results.append(result)

    return {
        "total_companies_tested": len(results),
        "results": results,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger.info("Starting Growth Signal Scoring Engine (P8-3)")
    test_results = run_tests()
    for r in test_results["results"]:
        logger.info(
            "Company %s: growth_score=%s, trend=%s, rate=%s%%",
            str(r["company_id"])[:8],
            r["growth_score"],
            r["hiring_trend"],
            r["growth_rate_pct"],
        )
    logger.info(
        "Complete: %d companies processed",
        test_results["total_companies_tested"],
    )


if __name__ == "__main__":
    main()
