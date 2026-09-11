# -*- coding: utf-8 -*-
"""APIFY-03: Apify webhook receiver testleri (mock'lu, ag yok)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch  # noqa: E402

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scripts.apify_webhook_receiver import (  # noqa: E402
    ApifyWebhookReceiver,
    ApifyError,
    _processed_runs,
)

SECRET = "test-webhook-secret"


@pytest.fixture(autouse=True)
def _reset_processed_runs(tmp_path, monkeypatch):
    """Her testin temiz idempotency state ile başlamasını sağlar.

    Hem in-memory _processed_runs hem de diskteki JSONL log dosyası
    tmp_path'e yönlendirilir; böylece testler birbirinden izole olur."""
    _processed_runs.clear()
    monkeypatch.setattr(
        "scripts.apify_webhook_receiver.WEBHOOK_EVENT_LOG",
        tmp_path / "webhook_events.jsonl",
    )
    yield
    _processed_runs.clear()


def make_receiver() -> ApifyWebhookReceiver:
    return ApifyWebhookReceiver(secret_token=SECRET)


def make_succeeded_payload(
    run_id: str = "run-abc123", dataset_id: str = "ds-xyz789"
) -> dict:
    return {
        "eventType": "ACTOR.RUN.SUCCEEDED",
        "actorRunId": run_id,
        "actorId": "ziyrak/kariyer-scraper",
        "resource": {
            "id": run_id,
            "actorId": "ziyrak/kariyer-scraper",
            "defaultDatasetId": dataset_id,
            "status": "SUCCEEDED",
        },
    }


def make_failed_payload(run_id: str = "run-fail001") -> dict:
    return {
        "eventType": "ACTOR.RUN.FAILED",
        "actorRunId": run_id,
        "actorId": "ziyrak/kariyer-scraper",
        "resource": {"id": run_id, "status": "FAILED"},
    }


class TestVerifySecret:
    def test_valid_secret(self) -> None:
        r = make_receiver()
        assert r.verify_secret(SECRET) is True

    def test_invalid_secret(self) -> None:
        r = make_receiver()
        assert r.verify_secret("wrong") is False

    def test_empty_secret(self) -> None:
        r = make_receiver()
        assert r.verify_secret("") is False

    def test_no_secret_configured_allows_all(self) -> None:
        r = ApifyWebhookReceiver(secret_token="")
        assert r.verify_secret("") is True
        assert r.verify_secret("anything") is True


class TestVerifyHmac:
    def test_valid_hmac(self) -> None:
        import hmac as _hmac
        import hashlib as _hashlib

        payload = b'{"test": true}'
        secret = "my-secret"
        sig = _hmac.new(secret.encode(), payload, _hashlib.sha256).hexdigest()
        assert (
            ApifyWebhookReceiver.verify_hmac(payload, f"sha256={sig}", secret) is True
        )

    def test_invalid_hmac(self) -> None:
        payload = b'{"test": true}'
        assert (
            ApifyWebhookReceiver.verify_hmac(payload, "sha256=fake", "real-secret")
            is False
        )

    def test_missing_signature(self) -> None:
        assert ApifyWebhookReceiver.verify_hmac(b"data", "", "secret") is False


class TestParseEvent:
    def test_succeeded_parse(self) -> None:
        r = make_receiver()
        payload = make_succeeded_payload()
        event = r.parse_event(payload)
        assert event.event_type == "ACTOR.RUN.SUCCEEDED"
        assert event.actor_run_id == "run-abc123"
        assert event.dataset_id == "ds-xyz789"
        assert event.status == "SUCCEEDED"

    def test_failed_parse(self) -> None:
        r = make_receiver()
        payload = make_failed_payload()
        event = r.parse_event(payload)
        assert event.event_type == "ACTOR.RUN.FAILED"
        assert event.actor_run_id == "run-fail001"
        assert event.status == "FAILED"


class TestIdempotency:
    def test_first_run_not_processed(self) -> None:
        r = make_receiver()
        assert r.is_processed("run-new") is False

    def test_second_run_processed(self) -> None:
        r = make_receiver()
        # First pass
        result = r.process_webhook(make_succeeded_payload("run-dup"), secret=SECRET)
        assert result["status"] == "ok"
        # Second pass — idempotent
        result2 = r.process_webhook(make_succeeded_payload("run-dup"), secret=SECRET)
        assert result2.get("message") == "already_processed"


class TestProcessWebhook:
    def test_rejected_bad_secret(self) -> None:
        r = make_receiver()
        result = r.process_webhook(make_succeeded_payload(), secret="wrong")
        assert result["status"] == "rejected"
        assert result["reason"] == "invalid_secret"

    def test_rejected_missing_run_id(self) -> None:
        r = make_receiver()
        result = r.process_webhook({"eventType": "ACTOR.RUN.SUCCEEDED"}, secret=SECRET)
        assert result["status"] == "rejected"
        assert result["reason"] == "missing_run_id"

    def test_succeeded_routes_to_handler(self) -> None:
        r = make_receiver()
        with patch.object(
            r, "handle_succeeded", return_value={"action": "succeeded_handler"}
        ) as mock:
            result = r.process_webhook(make_succeeded_payload(), secret=SECRET)
            mock.assert_called_once()
            assert result["status"] == "ok"

    def test_failed_routes_to_failure_handler(self) -> None:
        r = make_receiver()
        with patch.object(
            r,
            "handle_failure",
            return_value={"action": "failure_handler", "alerted": True},
        ) as mock:
            result = r.process_webhook(make_failed_payload(), secret=SECRET)
            mock.assert_called_once()
            assert result["status"] == "ok"

    def test_unknown_event_noop(self) -> None:
        r = make_receiver()
        payload = {
            "eventType": "ACTOR.RUN.CREATED",
            "actorRunId": "run-start01",
            "resource": {"id": "run-start01", "status": "RUNNING"},
        }
        result = r.process_webhook(payload, secret=SECRET)
        assert result["status"] == "ok"
        assert result["event_type"] == "ACTOR.RUN.CREATED"
        assert result.get("action") == "noop"


class TestHandleFailure:
    def test_error_ledger_and_telegram(self) -> None:
        r = make_receiver()
        event = r.parse_event(make_failed_payload())
        with patch(
            "scripts.apify_webhook_receiver._telegram_alert", return_value=True
        ) as mock_telegram:
            result = r.handle_failure(event)
            assert result["action"] == "failure_handler"
            assert result["alerted"] is True
            mock_telegram.assert_called_once()


class TestHandleSucceededNoClient:
    def test_succeeded_without_apify_client_triggers_ingest(self) -> None:
        r = make_receiver()
        event = r.parse_event(make_succeeded_payload())
        with patch.object(r, "_trigger_ingest") as mock_ingest:
            result = r.handle_succeeded(event)
            assert result["ingest_triggered"] is True
            mock_ingest.assert_called_once()


class TestHandleSucceededWithClient:
    def test_succeeded_with_mock_client(self) -> None:
        mock_client = MagicMock()
        mock_client.fetch_dataset_items.return_value = [
            {"title": "Developer", "url": "https://x.com/job/1"},
            {"title": "Engineer", "url": "https://x.com/job/2"},
        ]
        r = ApifyWebhookReceiver(secret_token=SECRET, apify_client=mock_client)
        event = r.parse_event(make_succeeded_payload())
        with patch.object(r, "_trigger_ingest") as mock_ingest:
            result = r.handle_succeeded(event)
            assert result["items_fetched"] == 2
            assert result["ingest_triggered"] is True
            mock_ingest.assert_called_once()

    def test_succeeded_dataset_error_logged(self) -> None:
        mock_client = MagicMock()
        mock_client.fetch_dataset_items.side_effect = ApifyError("API error")
        r = ApifyWebhookReceiver(secret_token=SECRET, apify_client=mock_client)
        event = r.parse_event(make_succeeded_payload())
        result = r.handle_succeeded(event)
        assert "error" in result


class TestEventLogger:
    def test_event_persisted_to_jsonl(self, tmp_path, monkeypatch) -> None:
        """Webhook event'leri JSONL'ye yazılır."""
        log_path = tmp_path / "webhook_events.jsonl"
        monkeypatch.setattr(
            "scripts.apify_webhook_receiver.WEBHOOK_EVENT_LOG",
            log_path,
        )
        r = ApifyWebhookReceiver(secret_token=SECRET)
        result = r.process_webhook(
            make_succeeded_payload("run-test-001"), secret=SECRET
        )
        assert result["status"] == "ok"
        assert log_path.exists()
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) >= 1
        entry = json.loads(lines[0])
        assert entry["actor_run_id"] == "run-test-001"


class TestIdempotencyPersistence:
    def test_processed_run_detected_after_restart(self, tmp_path, monkeypatch) -> None:
        """Process restart sonrası JSONL'den idempotency kontrolü."""
        log_path = tmp_path / "webhook_events.jsonl"
        monkeypatch.setattr(
            "scripts.apify_webhook_receiver.WEBHOOK_EVENT_LOG",
            log_path,
        )
        monkeypatch.setattr("scripts.apify_webhook_receiver._processed_runs", {})

        r1 = ApifyWebhookReceiver(secret_token=SECRET)
        r1.process_webhook(make_succeeded_payload("run-persist-001"), secret=SECRET)
        assert log_path.exists()

        # "Restart" — yeni receiver, ama JSONL kaydı var
        r2 = ApifyWebhookReceiver(secret_token=SECRET)
        assert r2.is_processed("run-persist-001") is True
