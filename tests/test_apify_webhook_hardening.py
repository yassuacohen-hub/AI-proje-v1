# -*- coding: utf-8 -*-
"""APIFY-03/P7-12: Apify webhook hardening birim testleri.

Kapsam:
- Token bucket rate limiting + retry_after
- Dead-letter queue (DLQ) yazma ve dogrulama
- Request validation (timestamp, HMAC, secret, payload type)
- Exponential backoff retry mekanizmasi
- Health endpoint metrikleri
- Prometheus metrics kayitlari
- End-to-end retry integration
- Rate limit response yapisi
- Idempotency + DLQ etkilesimi
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scripts.apify_webhook_receiver import (  # noqa: E402
    ApifyWebhookReceiver,
    _check_rate_limit,
    _processed_runs,
    _rate_limit_buckets,
    WEBHOOK_DLQ_LOG,
    WEBHOOK_EVENT_LOG,
)

SECRET = "test-webhook-secret-123"


@pytest.fixture(autouse=True)
def _reset_global_state(tmp_path, monkeypatch):
    _rate_limit_buckets.clear()
    _processed_runs.clear()
    monkeypatch.setattr(
        "scripts.apify_webhook_receiver.WEBHOOK_DLQ_LOG",
        tmp_path / "dlq.jsonl",
    )
    monkeypatch.setattr(
        "scripts.apify_webhook_receiver.WEBHOOK_EVENT_LOG",
        tmp_path / "events.jsonl",
    )
    yield
    _rate_limit_buckets.clear()
    _processed_runs.clear()


def make_receiver(**kwargs) -> ApifyWebhookReceiver:
    defaults = {"secret_token": SECRET, "enable_rate_limit": True}
    defaults.update(kwargs)
    return ApifyWebhookReceiver(**defaults)


def make_succeeded_payload(run_id: str = "run-hardening-01") -> dict:
    return {
        "eventType": "ACTOR.RUN.SUCCEEDED",
        "actorRunId": run_id,
        "actorId": "test/actor",
        "resource": {
            "id": run_id,
            "actorId": "test/actor",
            "defaultDatasetId": "ds-1",
            "status": "SUCCEEDED",
        },
    }


class TestRateLimiting:
    def test_ilk_istek_izne_verilir(self) -> None:
        allowed, _ = _check_rate_limit("token-abc")
        assert allowed is True

    def test_kapasite_asilirsa_reddedilir(self) -> None:
        token = "rate-token-full"
        for _ in range(100):
            _check_rate_limit(token)
        allowed, retry_after = _check_rate_limit(token)
        assert allowed is False
        assert retry_after > 0.0

    def test_anonymous_token_icin_limit_yok(self) -> None:
        r = make_receiver()
        allowed, retry_after = r.check_rate_limit("")
        assert allowed is True
        assert retry_after == 0.0

    def test_rate_limit_devre_disi_birakildi(self) -> None:
        r = make_receiver(enable_rate_limit=False)
        allowed, retry_after = r.check_rate_limit("tok")
        assert allowed is True
        assert retry_after == 0.0

    def test_bucket_refill_olur(self, monkeypatch: pytest.MonkeyPatch) -> None:
        token = "refill-token"
        _check_rate_limit(token)
        original_time = time.time
        monkeypatch.setattr(time, "time", lambda: original_time() + 5)
        allowed, retry_after = _check_rate_limit(token)
        assert allowed is True


class TestDeadLetterQueue:
    def test_dlq_validation_hatasinda_yazilir(self, tmp_path: Path) -> None:
        r = make_receiver()
        r._write_dlq({"bad": "payload"}, "not a dict", "validation_error")
        lines = (tmp_path / "dlq.jsonl").read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["error_type"] == "validation_error"
        assert entry["error"] == "not a dict"
        assert entry["payload"] == {"bad": "payload"}

    def test_dlq_auth_hatasinda_yazilir(self, tmp_path: Path) -> None:
        r = make_receiver()
        r._write_dlq({"x": 1}, "invalid secret", "auth_error")
        lines = (tmp_path / "dlq.jsonl").read_text(encoding="utf-8").strip().split("\n")
        entry = json.loads(lines[0])
        assert entry["error_type"] == "auth_error"

    def test_process_webhook_bad_payload_dlq_ile(self, tmp_path: Path) -> None:
        r = make_receiver()
        result = r.process_webhook("string-degil", secret=SECRET)
        assert result["status"] == "rejected"
        assert result["reason"] == "invalid_payload"
        lines = (tmp_path / "dlq.jsonl").read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1

    def test_dlq_zaman_damgasi_icerir(self, tmp_path: Path) -> None:
        r = make_receiver()
        r._write_dlq({}, "err", "type")
        lines = (tmp_path / "dlq.jsonl").read_text(encoding="utf-8").strip().split("\n")
        entry = json.loads(lines[0])
        assert "timestamp" in entry


class TestRequestValidation:
    def test_gecersiz_payload_turu_reddedilir(self) -> None:
        r = make_receiver()
        result = r.process_webhook(12345, secret=SECRET)
        assert result["status"] == "rejected"
        assert result["reason"] == "invalid_payload"

    def test_yanlis_secret_reddedilir(self) -> None:
        r = make_receiver()
        result = r.process_webhook(make_succeeded_payload(), secret="yanlis")
        assert result["status"] == "rejected"
        assert result["reason"] == "invalid_secret"

    def test_bos_secret_reddedilir(self) -> None:
        r = make_receiver()
        result = r.process_webhook(make_succeeded_payload(), secret="")
        assert result["status"] == "rejected"
        assert result["reason"] == "invalid_secret"

    def test_gecersiz_hmac_reddedilir(self) -> None:
        r = make_receiver()
        payload = make_succeeded_payload()
        result = r.process_webhook(
            payload, secret=SECRET, signature="sha256=fake-signature"
        )
        assert result["status"] == "rejected"
        assert result["reason"] == "invalid_hmac"

    def test_timestamp_skew_kontrolu(self, monkeypatch: pytest.MonkeyPatch) -> None:
        r = make_receiver()
        now = datetime.now(timezone.utc)
        past = (now - timedelta(seconds=400)).isoformat()
        payload = make_succeeded_payload()
        payload["createdAt"] = past
        result = r.process_webhook(payload, secret=SECRET)
        assert result["status"] == "rejected"
        assert result["reason"] == "timestamp_skew"

    def test_gecerli_timestamp_kabul_edilir(self) -> None:
        r = make_receiver()
        payload = make_succeeded_payload()
        payload["createdAt"] = datetime.now(timezone.utc).isoformat()
        result = r.process_webhook(payload, secret=SECRET)
        assert result["status"] == "ok"


class TestRetryBackoff:
    def test_basarili_ilk_deneme(self) -> None:
        r = make_receiver(max_retry_attempts=3)
        fn = MagicMock(return_value="sonuc")
        result = r.retry_with_backoff(fn, "a", b=2)
        assert result == "sonuc"
        fn.assert_called_once_with("a", b=2)

    def test_basaridan_sonra_retry(self) -> None:
        r = make_receiver(max_retry_attempts=3, base_backoff=0.01)
        fn = MagicMock(side_effect=[RuntimeError("gecici"), "ok"])
        with patch("time.sleep"):
            result = r.retry_with_backoff(fn)
        assert result == "ok"
        assert fn.call_count == 2

    def test_tum_denemeler_basarisiz(self) -> None:
        r = make_receiver(max_retry_attempts=2, base_backoff=0.01)
        fn = MagicMock(side_effect=RuntimeError("kalici"))
        with patch("time.sleep"), pytest.raises(RuntimeError, match="kalici"):
            r.retry_with_backoff(fn)
        assert fn.call_count == 2

    def test_backoff_suresi_artar(self) -> None:
        r = make_receiver(max_retry_attempts=4, base_backoff=1.0)
        sleeps = []
        fn = MagicMock(side_effect=[RuntimeError("e"), RuntimeError("e"), "ok"])

        def fake_sleep(s):
            sleeps.append(s)

        with patch("time.sleep", side_effect=fake_sleep):
            r.retry_with_backoff(fn)
        assert len(sleeps) == 2
        assert sleeps[1] > sleeps[0]


class TestHealthEndpoint:
    def test_health_anahtar_kelimeler(self) -> None:
        r = make_receiver()
        h = r.health_check()
        assert "status" in h
        assert "secret_configured" in h
        assert "rate_limit_enabled" in h
        assert "dlq_size" in h
        assert "processed_runs_memory" in h
        assert "prometheus_available" in h

    def test_health_durumu_healthy(self) -> None:
        r = make_receiver()
        assert r.health_check()["status"] == "healthy"

    def test_health_secret_durumu(self) -> None:
        r = make_receiver(secret_token="abc")
        assert r.health_check()["secret_configured"] is True

    def test_health_dlq_boyutu(self, tmp_path: Path) -> None:
        r = make_receiver()
        dlq = tmp_path / "dlq.jsonl"
        dlq.write_text("{\"x\": 1}\n{\"x\": 2}\n", encoding="utf-8")
        with patch(
            "scripts.apify_webhook_receiver.WEBHOOK_DLQ_LOG", dlq
        ):
            h = r.health_check()
        assert h["dlq_size"] == 2


class TestPrometheusMetrics:
    def test_metrics_cikti_turu(self) -> None:
        r = make_receiver()
        out = r.get_metrics()
        assert isinstance(out, bytes)

    def test_prometheus_yoksa_noop_mesaj(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "scripts.apify_webhook_receiver.PROMETHEUS_AVAILABLE", False
        )
        r = make_receiver()
        assert r.get_metrics() == b"# Prometheus client not installed\n"

    def test_metrics_uretimi(self) -> None:
        r = make_receiver()
        out = r.get_metrics()
        assert len(out) > 0


class TestRetryIntegration:
    def test_handle_succeeded_retry_icerir(self) -> None:
        mock_client = MagicMock()
        mock_client.fetch_dataset_items.side_effect = [
            RuntimeError("gecici api hatasi"),
            [{"title": "Stajyer"}],
        ]
        r = ApifyWebhookReceiver(secret_token=SECRET, apify_client=mock_client)
        event = r.parse_event(make_succeeded_payload())
        with patch.object(r, "_trigger_ingest"):
            result = r.handle_succeeded(event)
        assert result.get("items_fetched") == 1
        assert result.get("ingest_triggered") is True

    def test_retry_tukendiginde_hata_kayit_olusturulur(self) -> None:
        mock_client = MagicMock()
        mock_client.fetch_dataset_items.side_effect = RuntimeError("kalici hata")
        r = ApifyWebhookReceiver(
            secret_token=SECRET,
            apify_client=mock_client,
            max_retry_attempts=2,
            base_backoff=0.01,
        )
        event = r.parse_event(make_succeeded_payload())
        with patch.object(r, "_trigger_ingest"), patch(
            "scripts.apify_webhook_receiver._telegram_alert", return_value=True
        ) as mock_tg, patch.object(
            r._ledger, "add"
        ) as mock_add:
            result = r.handle_succeeded(event)
        assert "error" in result
        mock_add.assert_called_once()


class TestRateLimitHeaders:
    def test_rate_limited_retry_after_icerir(self) -> None:
        r = make_receiver()
        token = "header-token"
        for _ in range(100):
            _check_rate_limit(token)
        result = r.process_webhook(make_succeeded_payload(), secret=token)
        assert result["status"] == "rate_limited"
        assert "retry_after" in result
        assert isinstance(result["retry_after"], float)
        assert result["retry_after"] > 0.0

    def test_normal_istek_rate_limit_yok(self) -> None:
        r = make_receiver()
        result = r.process_webhook(make_succeeded_payload(), secret=SECRET)
        assert result.get("status") != "rate_limited"


class TestIdempotencyWithDLQ:
    def test_ikinci_istek_dlq_yazmaz(self, tmp_path: Path) -> None:
        r = make_receiver()
        payload = make_succeeded_payload("idem-run-01")
        r.process_webhook(payload, secret=SECRET)
        dlq_path = tmp_path / "dlq.jsonl"
        first_count = sum(1 for _ in dlq_path.open(encoding="utf-8")) if dlq_path.exists() else 0
        result2 = r.process_webhook(payload, secret=SECRET)
        assert result2.get("message") == "already_processed"
        second_count = sum(1 for _ in dlq_path.open(encoding="utf-8")) if dlq_path.exists() else 0
        assert second_count == first_count

    def test_basari_sonrasi_tekrar_basari(self) -> None:
        r = make_receiver()
        payload = make_succeeded_payload("idem-run-02")
        result1 = r.process_webhook(payload, secret=SECRET)
        assert result1["status"] == "ok"
        result2 = r.process_webhook(payload, secret=SECRET)
        assert result2["status"] == "ok"
        assert result2.get("message") == "already_processed"

    def test_olay_logu_tekrar_yazilmaz(self, tmp_path: Path) -> None:
        r = make_receiver()
        payload = make_succeeded_payload("idem-run-03")
        r.process_webhook(payload, secret=SECRET)
        lines = (tmp_path / "events.jsonl").read_text(encoding="utf-8").strip().split("\n")
        first_lines = len(lines) if lines[0] else 0
        r.process_webhook(payload, secret=SECRET)
        lines = (tmp_path / "events.jsonl").read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == first_lines
