# -*- coding: utf-8 -*-
"""P7-14: E2E Pipeline Test - Webhook -> ingest -> SignalAnalyzer -> IntelligenceScorer.

DB bagimliligi yok; get_engine() ve subprocess/Popen mock'lanir. Akis sirasi ve
veri transferi dogrulanir. CI'da (DATABASE_URL yokken) calisir.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.apify_webhook_receiver import (  # noqa: E402
    ApifyWebhookReceiver,
    _processed_runs,
    _rate_limit_buckets,
)
from scripts.ingest_job_postings import (  # noqa: E402
    ingest_job_postings,
)
from company_master.intelligence.job_intelligence.pipeline.analyzer import (  # noqa: E402
    SignalAnalyzer,
)
from company_master.intelligence.job_intelligence.pipeline.normalizer import (  # noqa: E402
    MatchResult,
)
from company_master.intelligence.job_intelligence.pipeline import (
    scorer as scorer_mod,
)  # noqa: E402

CID = uuid.uuid4()


class FakeResult:
    """conn.execute() sonucu; scalar/fetchall/mappings destegi."""

    def __init__(self, value=True):
        self._value = value
        self._rows = []

    def scalar(self):
        return self._value

    def scalar_one(self):
        return self._value

    def fetchall(self):
        return self._rows

    def first(self):
        return self._rows[0] if self._rows else None

    def one(self):
        return self._rows[0] if self._rows else None

    def all(self):
        return self._rows

    def mappings(self):
        return self


class FakeConn:
    """SQL'i kaydeden ve INSERT'leri kabul eden sahte connection."""

    def __init__(self, store=None):
        self.store = store if store is not None else {"sqls": [], "records": []}
        self.committed = False

    def execute(self, sql, params=None):
        self.store["sqls"].append(str(sql))
        text_sql = str(sql).lower()
        if "insert into job_postings" in text_sql:
            self.store["records"].append(("job_postings", params))
            return FakeResult(True)
        if "insert into company_signals" in text_sql:
            self.store["records"].append(("company_signals", params))
            return FakeResult(True)
        if "insert into company_intelligence_scores" in text_sql:
            self.store["records"].append(("company_intelligence_scores", params))
            return FakeResult(True)
        if "delete from company_signals" in text_sql:
            return FakeResult(True)
        if "select" in text_sql:
            return FakeResult(True)
        return FakeResult(True)

    def commit(self):
        self.committed = True

    def close(self):
        pass


class FakeEngine:
    """begin()/connect() saglayan ve store'u paylasan sahte engine."""

    def __init__(self):
        self.store = {"sqls": [], "records": []}

    def connect(self):
        return _Ctx(FakeConn(self.store))

    def begin(self):
        return _Ctx(FakeConn(self.store))


class _Ctx:
    def __init__(self, conn):
        self._conn = conn

    def __enter__(self):
        return self._conn

    def __exit__(self, *exc):
        if exc[0] is None:
            self._conn.commit()
        return False


class FakeMatcher:
    def __init__(self, result):
        self._result = result

    def match(self, raw_name=None, domain=None, tax_number=None, mersis=None):
        return self._result


@pytest.fixture(autouse=True)
def _e2e_state(tmp_path, monkeypatch):
    """Webhook log yollarini izole et; receiver state temizle."""
    import scripts.apify_webhook_receiver as recv_mod

    monkeypatch.setattr(recv_mod, "WEBHOOK_DLQ_LOG", tmp_path / "dlq.jsonl")
    monkeypatch.setattr(recv_mod, "WEBHOOK_EVENT_LOG", tmp_path / "events.jsonl")
    _processed_runs.clear()
    _rate_limit_buckets.clear()
    yield
    _processed_runs.clear()
    _rate_limit_buckets.clear()


def _succeeded_payload(run_id: str = "run-e2e-1") -> dict:
    return {
        "eventType": "ACTOR.RUN.SUCCEEDED",
        "actorRunId": run_id,
        "actorId": "ziyrak/kariyer-scraper",
        "resource": {
            "id": run_id,
            "actorId": "ziyrak/kariyer-scraper",
            "defaultDatasetId": "ds-e2e-1",
            "status": "SUCCEEDED",
        },
    }


# ---------------------------------------------------------------------------
# 1) Webhook -> ingest tetikleme
# ---------------------------------------------------------------------------


def test_webhook_succeeded_ingest_tetikler():
    """SUCCEEDED webhook, handle_succeeded uzerinden ingest tetikler."""
    receiver = ApifyWebhookReceiver(
        secret_token="test-secret", apify_client=None, enable_rate_limit=False
    )
    with patch.object(receiver, "_trigger_ingest") as mock_trigger:
        result = receiver.process_webhook(_succeeded_payload(), secret="test-secret")
    assert result["status"] == "ok"
    mock_trigger.assert_called_once()


def test_ingest_script_komutu_source_ve_input_icerir(tmp_path):
    """_trigger_ingest; --input ve --source apify parametrelerini verir."""
    import scripts.apify_webhook_receiver as recv_mod

    receiver = ApifyWebhookReceiver(enable_rate_limit=False)
    event = MagicMock()
    event.actor_run_id = "run-e2e-cmd"
    with patch.object(recv_mod.subprocess, "Popen") as mock_popen:
        receiver._trigger_ingest(event, input_file=str(tmp_path / "data.jsonl"))
    assert mock_popen.called
    cmd = mock_popen.call_args.args[0]
    assert "--input" in cmd
    assert str(tmp_path / "data.jsonl") in cmd
    assert "--source" in cmd
    assert "apify" in cmd


# ---------------------------------------------------------------------------
# 2) ingest_job_postings
# ---------------------------------------------------------------------------


def test_ingest_jsonl_den_job_postings_insert(tmp_path, monkeypatch):
    """JSONL kaydi job_postings INSERT'ine donusur (fake DB)."""
    import scripts.ingest_job_postings as ingest_mod

    source_file = tmp_path / "apify_e2e.jsonl"
    record = {
        "company_name": "Acme A.S.",
        "title": "Backend Engineer",
        "source_url": "https://acme.com/careers/1",
        "description": "Python gerekli",
        "posted_at": "2026-09-01T10:00:00Z",
        "technologies": ["python", "fastapi"],
    }
    source_file.write_text(
        json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    fake_engine = FakeEngine()
    monkeypatch.setattr(ingest_mod, "get_engine", lambda: fake_engine)
    monkeypatch.setattr(ingest_mod, "SOURCE_FILES", [("apify-e2e", source_file)])
    ok = MatchResult(
        company_id=CID, matched_name="Acme A.S.", match_type="fuzzy", confidence=0.95
    )
    monkeypatch.setattr(
        ingest_mod, "CompanyMatcher", lambda fuzzy_threshold=85.0: FakeMatcher(ok)
    )

    stats = ingest_job_postings()

    assert stats["matched"] == 1
    assert stats["inserted"] == 1
    types = [t for (t, _) in fake_engine.store["records"]]
    assert "job_postings" in types


# ---------------------------------------------------------------------------
# 3) SignalAnalyzer
# ---------------------------------------------------------------------------


def _make_posting(
    title: str = "Engineer",
    dept: str = "engineering",
    seniority: str = "senior",
    city: str = "Ankara",
    posted_at=None,
) -> dict:
    return {
        "job_posting_id": uuid.uuid4(),
        "company_id": CID,
        "title": title,
        "description": "",
        "department": dept,
        "seniority_level": seniority,
        "location_city": city,
        "technologies": json.dumps(["python"]),
        "posted_at": posted_at,
        "collected_at": None,
        "location_country": "Türkiye",
        "employment_type": "full-time",
        "remote_type": "onsite",
        "source_name": "apify-e2e",
        "source_url": "https://acme.com/careers/1",
        "external_id": "job-1",
        "raw_data": {},
    }


def test_analyzer_job_postings_den_sinyal_uretir(monkeypatch):
    """Analyzer; job_postings girdisinden sinyal uretir ve kaydeder."""
    analyzer = SignalAnalyzer(window_days=90)
    postings = [
        _make_posting(
            title="Engineer 1", posted_at=datetime.now(timezone.utc) - timedelta(days=2)
        ),
        _make_posting(
            title="Engineer 2", posted_at=datetime.now(timezone.utc) - timedelta(days=1)
        ),
        _make_posting(title="Engineer 3", posted_at=datetime.now(timezone.utc)),
    ]
    monkeypatch.setattr(analyzer, "_load_job_postings", lambda: postings)
    monkeypatch.setattr(analyzer, "_load_company_tech_profile", lambda cid: {})
    monkeypatch.setattr(analyzer, "_load_existing_locations", lambda cid: set())
    monkeypatch.setattr(analyzer, "_load_existing_departments", lambda cid: set())

    saved: list[dict] = []

    def _fake_save(signals):
        saved.extend(signals)
        return len(signals)

    monkeypatch.setattr(analyzer, "_save_signals", _fake_save)

    stats = analyzer.analyze()

    assert stats["signals_generated"] >= 1
    assert any(s["signal_type"] == "growth" for s in saved)
    assert any(s["signal_type"] == "geo_expansion" for s in saved)


# ---------------------------------------------------------------------------
# 4) IntelligenceScorer
# ---------------------------------------------------------------------------


def test_scorer_sinyal_verisinden_skor_uretir(monkeypatch):
    """Scorer; company_signals girdisinden intensity scores INSERT uretir."""
    signal = {
        "signal_id": uuid.uuid4(),
        "company_id": CID,
        "signal_type": "growth",
        "signal_subtype": "hiring_surge",
        "score": 80.0,
        "confidence": 90.0,
        "evidence": {"job_posting_ids": ["x"]},
        "detected_at": datetime.utcnow() - timedelta(days=1),
        "valid_until": None,
        "metadata": {},
    }
    fake_engine = FakeEngine()
    monkeypatch.setattr(scorer_mod, "get_engine", lambda: fake_engine)
    monkeypatch.setattr(scorer_mod, "_load_active_signals", lambda: [signal])

    result = scorer_mod.score_all_companies()

    assert result["processed"] == 1
    types = [t for (t, _) in fake_engine.store["records"]]
    assert "company_intelligence_scores" in types


# ---------------------------------------------------------------------------
# 5) Tam akis baglantisi
# ---------------------------------------------------------------------------


def test_tam_akis_webhook_analiz_skor_zinciri(tmp_path, monkeypatch):
    """Webhook -> analyzer sinyalleri -> scorer skorlari zinciri veri akisini dogrular."""
    receiver = ApifyWebhookReceiver(
        secret_token="test-secret", apify_client=None, enable_rate_limit=False
    )
    with patch.object(receiver, "_trigger_ingest"):
        w = receiver.process_webhook(_succeeded_payload(), secret="test-secret")
    assert w["status"] == "ok"

    analyzer = SignalAnalyzer(window_days=90)
    postings = [
        _make_posting(
            title="Engineer 1", posted_at=datetime.now(timezone.utc) - timedelta(days=2)
        ),
        _make_posting(
            title="Engineer 2", posted_at=datetime.now(timezone.utc) - timedelta(days=1)
        ),
        _make_posting(title="Engineer 3", posted_at=datetime.now(timezone.utc)),
    ]
    monkeypatch.setattr(analyzer, "_load_job_postings", lambda: postings)
    monkeypatch.setattr(analyzer, "_load_company_tech_profile", lambda cid: {})
    monkeypatch.setattr(analyzer, "_load_existing_locations", lambda cid: set())
    monkeypatch.setattr(analyzer, "_load_existing_departments", lambda cid: set())

    saved: list[dict] = []

    def _fake_save(signals):
        for sig in signals:
            sig.setdefault("signal_id", uuid.uuid4())
            sig.setdefault("detected_at", datetime.utcnow() - timedelta(days=1))
        saved.extend(signals)
        return len(signals)

    monkeypatch.setattr(analyzer, "_save_signals", _fake_save)
    a_stats = analyzer.analyze()
    assert a_stats["signals_generated"] >= 1
    assert any(s["signal_type"] == "growth" for s in saved)

    fake_engine = FakeEngine()
    monkeypatch.setattr(scorer_mod, "get_engine", lambda: fake_engine)
    monkeypatch.setattr(scorer_mod, "_load_active_signals", lambda: saved)

    result = scorer_mod.score_all_companies()

    assert result["processed"] == 1
    types = [t for (t, _) in fake_engine.store["records"]]
    assert "company_intelligence_scores" in types
