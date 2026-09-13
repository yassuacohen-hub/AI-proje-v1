# -*- coding: utf-8 -*-
"""YENI-5: Apify Webhook DLQ Monitor testleri."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from src.company_master.intelligence.job_intelligence.pipeline.dlq_monitor import (
    ApifyDLQMonitor,
    DLQEntry,
)


@pytest.fixture
def sample_dlq_file():
    entries = [
        {"timestamp": "2026-09-11T11:43:36", "error_type": "auth_error", "error": "invalid secret", "payload": {"actorRunId": "run-1", "actorId": "ziyrak/kariyer-scraper", "eventType": "ACTOR.RUN.SUCCEEDED"}},
        {"timestamp": "2026-09-11T12:00:00", "error_type": "validation_error", "error": "missing actor_run_id", "payload": {"actorRunId": "run-3", "actorId": "ziyrak/kariyer-scraper", "eventType": "ACTOR.RUN.SUCCEEDED"}},
        {"timestamp": "2026-09-12T10:00:00", "error_type": "auth_error", "error": "invalid hmac", "payload": {"actorRunId": "run-2", "actorId": "ziyrak/other-scraper", "eventType": "ACTOR.RUN.FAILED"}},
    ]
    with NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        f.flush()
        yield f.name
    Path(f.name).unlink(missing_ok=True)


class TestDLQEntry:
    def test_entry_basic(self):
        data = {"timestamp": "2026-09-11T11:43:36", "error_type": "auth_error", "error": "invalid secret", "payload": {"actorRunId": "run-1"}}
        entry = DLQEntry(data)
        assert entry.error_type == "auth_error"
        assert entry.error == "invalid secret"
        assert entry.actor_run_id == "run-1"
        assert entry.event_type == ""

    def test_entry_to_dict(self):
        data = {"timestamp": "2026-09-11T11:43:36", "error_type": "auth_error", "error": "invalid secret", "payload": {"actorRunId": "run-1"}}
        entry = DLQEntry(data)
        d = entry.to_dict()
        assert d["error_type"] == "auth_error"
        assert "age_hours" in d
        assert isinstance(d["age_hours"], float) or d["age_hours"] is None


class TestApifyDLQMonitor:
    def test_load_entries(self, sample_dlq_file):
        monitor = ApifyDLQMonitor(dlq_path=sample_dlq_file)
        assert monitor.total_count() == 3

    def test_error_type_counts(self, sample_dlq_file):
        monitor = ApifyDLQMonitor(dlq_path=sample_dlq_file)
        counts = monitor.error_type_counts()
        assert counts["auth_error"] == 2
        assert counts["validation_error"] == 1

    def test_entries_by_error_type(self, sample_dlq_file):
        monitor = ApifyDLQMonitor(dlq_path=sample_dlq_file)
        auth_entries = monitor.entries_by_error_type("auth_error")
        assert len(auth_entries) == 2
        val_entries = monitor.entries_by_error_type("validation_error")
        assert len(val_entries) == 1

    def test_entries_by_actor(self, sample_dlq_file):
        monitor = ApifyDLQMonitor(dlq_path=sample_dlq_file)
        actor_entries = monitor.entries_by_actor("ziyrak/kariyer-scraper")
        assert len(actor_entries) == 2
        actor_entries2 = monitor.entries_by_actor("ziyrak/other-scraper")
        assert len(actor_entries2) == 1

    def test_summary(self, sample_dlq_file):
        monitor = ApifyDLQMonitor(dlq_path=sample_dlq_file)
        summary = monitor.summary()
        assert summary["total"] == 3
        assert summary["auth_errors"] == 2
        assert summary["validation_errors"] == 1
        assert summary["unique_actors"] == 2
        assert "ACTOR.RUN.SUCCEEDED" in summary["unique_event_types"]

    def test_format_report(self, sample_dlq_file):
        monitor = ApifyDLQMonitor(dlq_path=sample_dlq_file)
        report = monitor.format_report()
        assert "DLQ Raporu" in report
        assert "Toplam DLQ Kaydı" in report
        assert "auth_error" in report
        assert "validation_error" in report

    def test_format_report_verbose(self, sample_dlq_file):
        monitor = ApifyDLQMonitor(dlq_path=sample_dlq_file)
        report = monitor.format_report(verbose=True)
        assert "[0]" in report
        assert "[2]" in report

    def test_recent_entries(self, sample_dlq_file):
        monitor = ApifyDLQMonitor(dlq_path=sample_dlq_file)
        recent = monitor.recent_entries(hours=8760)
        assert len(recent) == 3

    def test_clear_dlq(self, sample_dlq_file):
        monitor = ApifyDLQMonitor(dlq_path=sample_dlq_file)
        assert monitor.total_count() == 3
        count = monitor.clear_dlq()
        assert count == 3
        assert monitor.total_count() == 0

    def test_empty_dlq(self):
        with NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
            f.write("")
            f.flush()
            path = f.name
        monitor = ApifyDLQMonitor(dlq_path=path)
        assert monitor.total_count() == 0
        assert monitor.summary()["total"] == 0
        Path(path).unlink(missing_ok=True)

    def test_retry_entry_out_of_range(self, sample_dlq_file):
        monitor = ApifyDLQMonitor(dlq_path=sample_dlq_file)
        result = monitor.retry_entry(999)
        assert result["success"] is False

    def test_nonexistent_dlq(self):
        monitor = ApifyDLQMonitor(dlq_path="/nonexistent/path/dlq.jsonl")
        assert monitor.total_count() == 0
        assert monitor.summary()["total"] == 0
