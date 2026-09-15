# -*- coding: utf-8 -*-
"""Growth Signal Scoring Engine - P8-3.

Is ilani verilerinden buyume sinyalleri tespit eder, skorlar ve
company_intelligence_scores.growth_score alanini doldurur.

Bes sinyal: ilan artisi, yeni sehir, yeni departman, yonetici ise alimi,
satis ekip genislesmesi. Her sinyal 0-100 skor ve guven (confidence) uretir.
Ayriliklar: Growth 0.30, Investment 0.25, Tech 0.20, Geo 0.15, Org 0.10.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

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


@dataclass
class SignalResult:
    signal_type: str
    signal_subtype: str
    score: float = 0.0
    confidence: float = 0.0
    evidence: dict[str, Any] = field(default_factory=dict)
    threshold_breached: str | None = None


_THRESHOLDS: dict[str, Any] = {
    "hiring_surge": {
        ">=50pct_increase": {"min_growth_rate": 50, "score": 100},
        "20-49pct_increase": {"min_growth_rate": 20, "score": 80},
        "10-19pct_increase": {"min_growth_rate": 10, "score": 60},
        "0-9pct_increase": {"min_growth_rate": 0, "score": 40},
        "<0pct_decline": {"max_growth_rate": 0, "score_formula": "40 * (1 + rate/100), clamped [0,39]"},
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
}CONTENT_PLACEHOLDER