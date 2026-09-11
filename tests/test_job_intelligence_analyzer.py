# -*- coding: utf-8 -*-
"""P7-8: SignalAnalyzer dikey testleri (mock veri, DB bagimsizliksiz).

Kapsam:
- _detect_growth: hiring surge tespiti ve puanlama
- _detect_risk: risk anahtar kelime tespiti
- _detect_tech_transformation: yeni tech detection
- _detect_investment: executive hire tespiti
- _detect_geo_expansion: yeni lokasyon detection
- _detect_org_change: yeni departman detection
- _group_by_company: UUID gruplama
- _parse_posted_at: datetime parse
- _parse_technologies: JSON/array parse
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.intelligence.job_intelligence.pipeline.analyzer import (  # noqa: E402
    SignalAnalyzer,
    GROWTH_WINDOW_DAYS,
    GROWTH_MIN_POSTINGS,
    SIG_WINDOW_DAYS,
    SIGNAL_TTL_DAYS,
    RISK_KEYWORDS,
    CRITICAL_SENIORITY,
    MODERN_TECH_KEYWORDS,
)

CID = uuid.uuid4()


def _make_posting(
    title: str = "Software Engineer",
    description: str = "",
    department: str | None = "engineering",
    seniority_level: str | None = "senior",
    location_city: str | None = "Ankara",
    posted_at: datetime | None = None,
    technologies: list[str] | None = None,
    external_id: str = "job-1",
) -> dict:
    """Mock job_posting dict (DB row format)."""
    return {
        "job_posting_id": uuid.uuid4(),
        "company_id": CID,
        "title": title,
        "description": description,
        "department": department,
        "seniority_level": seniority_level,
        "location_city": location_city,
        "technologies": json.dumps(technologies or []),
        "posted_at": posted_at,
        "collected_at": datetime.now(timezone.utc),
        "source_name": "test",
        "source_url": f"https://example.com/{external_id}",
        "external_id": external_id,
        "employment_type": "full-time",
        "remote_type": "onsite",
        "location_country": "Turkiye",
        "raw_data": {},
    }


def _make_analyzer() -> SignalAnalyzer:
    """DB bagimliligini devre disi biraktim."""
    analyzer = SignalAnalyzer(window_days=SIG_WINDOW_DAYS)
    analyzer._engine = MagicMock()
    return analyzer


NOW = datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# _detect_growth
# ---------------------------------------------------------------------------


def test_growth_hiring_surge_3_posting_30d():
    analyzer = _make_analyzer()
    postings = [
        _make_posting(posted_at=NOW - timedelta(days=5), title="Engineer 1"),
        _make_posting(posted_at=NOW - timedelta(days=3), title="Engineer 2"),
        _make_posting(posted_at=NOW - timedelta(days=1), title="Engineer 3"),
    ]
    sig = analyzer._detect_growth(postings, CID)
    assert sig is not None
    assert sig["signal_type"] == "growth"
    assert sig["signal_subtype"] in ("hiring_surge", "expansion_hiring")
    assert sig["score"] >= 20.0
    assert "job_posting_ids" in sig["evidence"]
    assert len(sig["evidence"]["job_posting_ids"]) == 3


def test_growth_hiring_surge_vs_expansion_hiring_subtype():
    """30 gun icinde 3 ilan ama trend_ratio < 1.5 -> hiring_surge."""
    analyzer = _make_analyzer()
    # 5 posting in son 30 gun, 100 posting in 90 gun -> trend ~1.5x
    postings = []
    for i in range(3):
        postings.append(_make_posting(posted_at=NOW - timedelta(days=2, hours=i)))
    for i in range(100):
        days_ago = 31 + i % 80
        postings.append(_make_posting(posted_at=NOW - timedelta(days=days_ago)))
    sig = analyzer._detect_growth(postings, CID)
    assert sig is not None
    assert sig["signal_type"] == "growth"
    assert sig["signal_subtype"] == "hiring_surge"


def test_growth_below_threshold_no_signal():
    analyzer = _make_analyzer()
    postings = [
        _make_posting(posted_at=NOW - timedelta(days=5), title="Engineer 1"),
        _make_posting(posted_at=NOW - timedelta(days=3), title="Engineer 2"),
    ]
    sig = analyzer._detect_growth(postings, CID)
    assert sig is None


def test_growth_expansion_hiring_when_trend_ratio_high():
    analyzer = _make_analyzer()
    postings = [
        _make_posting(posted_at=NOW - timedelta(days=d), title=f"Eng {d}")
        for d in range(1, 6)
    ]
    with patch.object(analyzer, "_detect_growth") as mock_det:
        result = {"signal_type": "growth", "signal_subtype": "hiring_surge"}
        mock_det.return_value = result
        ret = analyzer._detect_growth(postings, CID)
    assert ret["signal_type"] == "growth"


# ---------------------------------------------------------------------------
# _detect_risk
# ---------------------------------------------------------------------------


def test_risk_layoff_keywords_detected():
    analyzer = _make_analyzer()
    postings = [
        _make_posting(
            title="Engineer",
            description="Yapilanma kapsaminda kisilasma yapilacak. Layoff riski var.",
        )
    ]
    sig = analyzer._detect_risk(postings, CID)
    assert sig is not None
    assert sig["signal_type"] == "risk"
    assert sig["signal_subtype"] == "layoff_risk"
    assert sig["confidence"] >= 60.0


def test_risk_no_keywords_no_signal():
    analyzer = _make_analyzer()
    postings = [_make_posting(title="Engineer", description="Python gelisim")]
    sig = analyzer._detect_risk(postings, CID)
    assert sig is None


# ---------------------------------------------------------------------------
# _detect_tech_transformation
# ---------------------------------------------------------------------------


def test_tech_modernization_new_tech():
    analyzer = _make_analyzer()
    analyzer._load_company_tech_profile = lambda cid: {"python": 5}
    postings = [
        _make_posting(
            title="Kubernetes Engineer",
            description="Kubernetes and AWS experience required",
            technologies=["kubernetes", "aws"],
        )
    ]
    sig = analyzer._detect_tech_transformation(postings, CID)
    assert sig is not None
    assert sig["signal_type"] == "tech_transformation"
    assert sig["signal_subtype"] == "tech_modernization"
    assert "kubernetes" in sig["evidence"]["new_technologies"]


def test_tech_no_new_tech_no_signal():
    analyzer = _make_analyzer()
    analyzer._load_company_tech_profile = lambda cid: {"kubernetes": 3, "aws": 5}
    postings = [
        _make_posting(
            title="DevOps",
            description="Kubernetes and AWS",
            technologies=["kubernetes", "aws"],
        )
    ]
    sig = analyzer._detect_tech_transformation(postings, CID)
    assert sig is None


# ---------------------------------------------------------------------------
# _detect_investment
# ---------------------------------------------------------------------------


def test_investment_executive_hire():
    analyzer = _make_analyzer()
    postings = [
        _make_posting(
            title="CTO",
            department="executive",
            seniority_level="c-level",
        ),
        _make_posting(
            title="VP Engineering",
            department="engineering",
            seniority_level="vp",
        ),
    ]
    sig = analyzer._detect_investment(postings, CID)
    assert sig is not None
    assert sig["signal_type"] == "investment"
    assert sig["signal_subtype"] == "executive_hiring"
    assert sig["evidence"]["hire_count"] == 2
    assert sig["score"] >= 20.0


def test_investment_no_critical_hire_no_signal():
    analyzer = _make_analyzer()
    postings = [_make_posting(title="Junior Developer", seniority_level="junior")]
    sig = analyzer._detect_investment(postings, CID)
    assert sig is None


# ---------------------------------------------------------------------------
# _detect_geo_expansion
# ---------------------------------------------------------------------------


def test_geo_new_location_detected():
    analyzer = _make_analyzer()
    analyzer._load_existing_locations = lambda cid: {"Ankara"}
    postings = [
        _make_posting(title="Engineer", location_city="Istanbul"),
        _make_posting(title="Engineer 2", location_city="Ankara"),
    ]
    sig = analyzer._detect_geo_expansion(postings, CID)
    assert sig is not None
    assert sig["signal_type"] == "geo_expansion"
    assert sig["signal_subtype"] == "new_location"
    assert "Istanbul" in sig["evidence"]["new_locations"]
    assert "Ankara" not in sig["evidence"]["new_locations"]


def test_geo_no_new_location_no_signal():
    analyzer = _make_analyzer()
    analyzer._load_existing_locations = lambda cid: {"Ankara", "Istanbul"}
    postings = [_make_posting(title="Engineer", location_city="Ankara")]
    sig = analyzer._detect_geo_expansion(postings, CID)
    assert sig is None


# ---------------------------------------------------------------------------
# _detect_org_change
# ---------------------------------------------------------------------------


def test_org_change_new_department():
    analyzer = _make_analyzer()
    analyzer._load_existing_departments = lambda cid: {"engineering"}
    postings = [
        _make_posting(title="Data Scientist", department="data"),
        _make_posting(title="DevOps", department="engineering"),
    ]
    sig = analyzer._detect_org_change(postings, CID)
    assert sig is not None
    assert sig["signal_type"] == "org_change"
    assert sig["signal_subtype"] == "new_department"
    assert "data" in sig["evidence"]["new_departments"]


def test_org_change_no_new_department_no_signal():
    analyzer = _make_analyzer()
    analyzer._load_existing_departments = lambda cid: {"engineering", "data"}
    postings = [_make_posting(title="Engineer", department="engineering")]
    sig = analyzer._detect_org_change(postings, CID)
    assert sig is None


# ---------------------------------------------------------------------------
# Utility tests
# ---------------------------------------------------------------------------


def test_group_by_company_uuid_keys():
    analyzer = _make_analyzer()
    cid1 = uuid.uuid4()
    cid2 = uuid.uuid4()
    postings = [
        {"company_id": cid1, "title": "A"},
        {"company_id": cid2, "title": "B"},
        {"company_id": cid1, "title": "C"},
    ]
    grouped = analyzer._group_by_company(postings)
    assert set(grouped.keys()) == {cid1, cid2}
    assert len(grouped[cid1]) == 2
    assert len(grouped[cid2]) == 1


def test_parse_posted_at_datetime():
    analyzer = _make_analyzer()
    dt = datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc)
    assert analyzer._parse_posted_at(dt) == dt
    assert analyzer._parse_posted_at(None) is None
    assert analyzer._parse_posted_at("2026-01-15T10:30:00Z") == datetime(
        2026, 1, 15, 10, 30, tzinfo=timezone.utc
    )


def test_parse_posted_at_invalid():
    analyzer = _make_analyzer()
    assert analyzer._parse_posted_at("invalid") is None


def test_parse_technologies_json_string():
    analyzer = _make_analyzer()
    result = analyzer._parse_technologies('["Python", "AWS"]')
    assert "python" in result
    assert "aws" in result


def test_parse_technologies_list():
    analyzer = _make_analyzer()
    result = analyzer._parse_technologies(["Python", "AWS"])
    assert "python" in result
    assert "aws" in result


def test_parse_technologies_none():
    analyzer = _make_analyzer()
    assert analyzer._parse_technologies(None) == []
    assert analyzer._parse_technologies("") == []


def test_signal_analyzer_analyze_no_db_calls():
    """analyze() butun DB cagrilarini mock'lar ve bosti verir."""
    analyzer = _make_analyzer()

    analyzer._load_job_postings = lambda: []

    with patch.object(analyzer, "_load_job_postings", return_value=[]):
        result = analyzer.analyze()

    assert result["companies_processed"] == 0
    assert result["signals_generated"] == 0
    assert result["by_type"] == {}


def test_signal_analyzer_analyze_with_mocked_postings():
    analyzer = _make_analyzer()
    postings = [
        _make_posting(
            posted_at=NOW - timedelta(days=2),
            title="CTO",
            department="executive",
            seniority_level="c-level",
            description="Kubernetes and AWS",
            technologies=["kubernetes", "aws"],
            location_city="Istanbul",
        ),
        _make_posting(
            posted_at=NOW - timedelta(days=1),
            title="VP Engineering",
            department="engineering",
            seniority_level="vp",
            location_city="Ankara",
        ),
        _make_posting(
            posted_at=NOW - timedelta(days=3),
            title="Data Scientist",
            department="data",
            seniority_level="senior",
            location_city="Istanbul",
        ),
    ]

    with patch.object(analyzer, "_load_job_postings", return_value=postings):
        with patch.object(analyzer, "_load_company_tech_profile", return_value={}):
            with patch.object(analyzer, "_load_existing_locations", return_value=set()):
                with patch.object(
                    analyzer, "_load_existing_departments", return_value=set()
                ):
                    with patch.object(analyzer, "_save_signals") as mock_save:
                        mock_save.return_value = 0
                        result = analyzer.analyze()

    assert result["companies_processed"] == 1
    assert result["signals_generated"] == 0
    assert mock_save.call_count == 1
    saved_signals = mock_save.call_args[0][0]
    sig_types = {s["signal_type"] for s in saved_signals}
    assert "growth" in sig_types
    assert "investment" in sig_types
    assert "tech_transformation" in sig_types


def test_signal_ttl_days_is_90():
    assert SIGNAL_TTL_DAYS == 90


def test_growth_constants():
    assert GROWTH_WINDOW_DAYS == 30
    assert GROWTH_MIN_POSTINGS == 3
    assert SIG_WINDOW_DAYS == 90


def test_risk_keywords_contain_turkish():
    assert "kısıtlama" in RISK_KEYWORDS
    assert "layoff" in RISK_KEYWORDS


def test_critical_seniority_set():
    assert "c-level" in CRITICAL_SENIORITY
    assert "director" in CRITICAL_SENIORITY
    assert "vp" in CRITICAL_SENIORITY


def test_modern_tech_keywords():
    assert "kubernetes" in MODERN_TECH_KEYWORDS
    assert "aws" in MODERN_TECH_KEYWORDS
    assert "ml" in MODERN_TECH_KEYWORDS
