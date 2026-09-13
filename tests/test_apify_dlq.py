# -*- coding: utf-8 -*-
"""P7-22: Apify Dead-Letter Queue (DLQ) ve Yeniden Deneme Akısı testleri.

Kapsam:
- DLQ yazma ve okuma
- DLQ boyutu ve hata türü raporlama
- Exponential backoff retry (başarılı ve başarısız)
- Retry bitişinde istisna fırlatma
- process_webhook ile DLQ entegrasyonu
- Webhook hardening testlerinde DLQ kapsamı
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.apify_webhook_receiver import (  # noqa: E402
    ApifyWebhookReceiver,
    _check_rate_limit,
    _rate_limit_buckets,
    _processed_runs,
    WEBHOOK_DLQ_LOG,
)

SECRET = "test-webhook-secret-dlq"


@pytest.fixture(autouse=True)
def _reset_state(tmp_path, monkeypatch):
    _rate_limit_buckets.clear()
    _processed_runs.clear()
    monkeypatch.setattr(
        "scripts.apify_webhook_receiver.WEBHOOK_DLQ_LOG",
        tmp_path / "dlq.jsonl",
    )
    yield
    _rate_limit_buckets.clear()
    _processed_runs.clear()


def make_receiver(**kwargs) -> ApifyWebhookReceiver:
    defaults = {"secret_token": SECRET, "enable_rate_limit": True}
    defaults.update(kwargs)
    return ApifyWebhookReceiver(**defaults)


class TestDeadLetterQueue:
    def test_dlq_yazma(self, tmp_path: Path) -> None:
        r = make_receiver()
        r._write_dlq({"raw": "payload"}, "test error", "test_type")
        lines = (tmp_path / "dlq.jsonl").read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["error_type"] == "test_type"
        assert entry["error"] == "test error"
        assert entry["payload"] == {"raw": "payload"}
        assert "timestamp" in entry

    def test_dlq_boyutu(self, tmp_path: Path) -> None:
        r = make_receiver()
        assert r._write_dlq({"a": 1}, "e1", "t1") is None
        assert r._write_dlq({"b": 2}, "e2", "t2") is None
        assert r._write_dlq({"c": 3}, "e3", "t1") is None
        lines = (tmp_path / "dlq.jsonl").read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3

    def test_dlq_hata_tur_raporlama(self, tmp_path: Path) -> None:
        r = make_receiver()
        r._write_dlq({}, "auth", "auth_error")
        r._write_dlq({}, "val", "validation_error")
        r._write_dlq({}, "auth2", "auth_error")
        lines = (tmp_path / "dlq.jsonl").read_text(encoding="utf-8").strip().split("\n")
        counts = {}
        for ln in lines:
            entry = json.loads(ln)
            et = entry["error_type"]
            counts[et] = counts.get(et, 0) + 1
        assert counts == {"auth_error": 2, "validation_error": 1}

    def test_process_webhook_string_payload_dlq(self, tmp_path: Path) -> None:
        r = make_receiver()
        result = r.process_webhook("string-degil", secret=SECRET)
        assert result["status"] == "rejected"
        assert result["reason"] == "invalid_payload"
        lines = (tmp_path / "dlq.jsonl").read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["error_type"] == "validation_error"

    def test_dlq_zaman_damgati(self, tmp_path: Path) -> None:
        r = make_receiver()
        r._write_dlq({}, "err", "type")
        entry = json.loads(
            (tmp_path / "dlq.jsonl").read_text(encoding="utf-8").strip()
        )
        assert "timestamp" in entry

    def test_dlq_tekrarlanabilir(self, tmp_path: Path) -> None:
        r = make_receiver()
        for _ in range(5):
            r._write_dlq({}, "err", "transient")
        lines = (tmp_path / "dlq.jsonl").read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 5


class TestRetryBackoff:
    def test_basarili_ilk_deneme(self) -> None:
        r = make_receiver(max_retry_attempts=3)
        fn = MagicMock(return_value="sonuc")
        result = r.retry_with_backoff(fn, "a", b=2)
        assert result == "sonuc"
        fn.assert_called_once_with("a", b=2)

    def test_retry_basarisiz_bitince_istisna(self) -> None:
        r = make_receiver(max_retry_attempts=3, base_backoff=0.01)
        fn = MagicMock(side_effect=RuntimeError("transient"))
        with pytest.raises(RuntimeError, match="transient"):
            r.retry_with_backoff(fn)
        assert fn.call_count == 3

    def test_exponential_backoff_beklentisi(self) -> None:
        r = make_receiver(max_retry_attempts=4, base_backoff=0.01)
        fn = MagicMock(side_effect=RuntimeError("x"))
        sleep_patched = []
        with patch("time.sleep", side_effect=lambda s: sleep_patched.append(s)):
            with pytest.raises(RuntimeError):
                r.retry_with_backoff(fn)
        expected = [0.01, 0.02, 0.04]
        assert sleep_patched == expected
        assert fn.call_count == 4

    def test_retry_basarili_ikinci_denemeyle(self) -> None:
        r = make_receiver(max_retry_attempts=3, base_backoff=0.01)
        side_effects = [RuntimeError("deneme 1"), "basarili"]
        fn = MagicMock(side_effect=side_effects)
        result = r.retry_with_backoff(fn)
        assert result == "basarili"
        assert fn.call_count == 2

    def test_rate_limit_sinir_dogrulanir(self) -> None:
        token = "rate-token-full"
        for _ in range(100):
            _check_rate_limit(token)
        allowed, retry_after = _check_rate_limit(token)
        assert allowed is False
        assert retry_after > 0.0

    def test_rate_limit_refill(self, monkeypatch: pytest.MonkeyPatch) -> None:
        token = "refill-token"
        _check_rate_limit(token)
        original_time = time.time
        monkeypatch.setattr(time, "time", lambda: original_time() + 5)
        allowed, retry_after = _check_rate_limit(token)
        assert allowed is True


class TestDlqWebhookIntegration:
    def test_basarili_islem_dlq_olusturmaz(self, tmp_path: Path) -> None:
        r = make_receiver()
        with patch.object(r, "handle_succeeded", return_value={"status": "ok"}):
            result = r.process_webhook({"eventType": "ACTOR.RUN.SUCCEEDED", "actorRunId": "run-ok"}, secret=SECRET)
        assert result["status"] == "ok"
        dlq_path = tmp_path / "dlq.jsonl"
        if dlq_path.exists():
            lines = dlq_path.read_text(encoding="utf-8").strip().split("\n")
            assert lines == [""]

    def test_islem_idempotent(self) -> None:
        r = make_receiver()
        payload = {"eventType": "ACTOR.RUN.SUCCEEDED", "actorRunId": "run-idem"}
        with patch.object(r, "handle_succeeded", return_value={"status": "ok"}):
            r.process_webhook(payload, secret=SECRET)
            r.process_webhook(payload, secret=SECRET)
        # Idempotency kontrolü _processed_runs'ta kalır
        assert r.is_processed("run-idem") is True

    def test_dlq_auth_hatasinda_yazar(self, tmp_path: Path) -> None:
        r = make_receiver()
        payload = {"eventType": "ACTOR.RUN.SUCCEEDED", "actorRunId": "run-auth"}
        result = r.process_webhook(payload, secret="yanlis")
        assert result["status"] == "rejected"
        assert result["reason"] == "invalid_secret"
        lines = (tmp_path / "dlq.jsonl").read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["error_type"] == "auth_error"
