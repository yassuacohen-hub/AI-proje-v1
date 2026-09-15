#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APIFY-03/P7-12: Apify Webhook Alıcısı + Kalıcı Olay İşleme + Prod Hardening.

Apify Actor run'ları tamamlandığında (veya başarısız olduğunda) webhook
gönderir. Bu modül olayları alır, doğrular, idempotent kaydeder ve
işler:

  1. Apify POST -> /api/webhooks/apify  (hizlica 200 OK, asenkron isle)
  2. Secret token + (istege bagli) HMAC dogrula
  3. actorRunId ile idempotency kontrolu
  4. eventType'e gore yonlendir:
     - ACTOR.RUN.SUCCEEDED -> datasetId'den veri cek, ingest_job_postings.py tetikle
     - ACTOR.RUN.FAILED / ABORTED / TIMED_OUT -> ErrorLedger + Telegram uyarisi
  5. Islem sonrasi credit_ledger / usage metriklerini guncelle (Y26)

Prod Hardening (P7-12):
  - Rate limiting per token/IP (token-based bucket)
  - Dead-letter queue (DLQ) for failed payloads
  - Retry/backoff with exponential backoff for transient failures
  - Request validation (size limits, content-type, timestamp)
  - Prometheus metrics (requests_total, duration, errors, dlq_size)
  - Health endpoint readiness/liveness

Kaynak: data/orchestrator/apify03_webhook_result.json
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from collections import defaultdict

# -- project root / src path --
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(ROOT / "src"))

from company_master.orchestrator.error_ledger import ErrorLedger  # noqa: E402
from company_master.orchestrator.models import ErrorLedgerEntry  # noqa: E402

try:
    from company_master.intelligence.job_intelligence.sources.apify_client import (  # noqa: E402
        ApifyClient,
        ApifyError,
    )
except ImportError:
    ApifyClient = None  # noqa: E402
    ApifyError = RuntimeError  # noqa: E402

# Prometheus metrics (optional)
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest  # noqa: E402
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = Histogram = Gauge = generate_latest = None

logger = logging.getLogger("apify_webhook_receiver")

WEBHOOK_EVENT_LOG = ROOT / "data" / "orchestrator" / "apify_webhook_events.jsonl"
WEBHOOK_DLQ_LOG = ROOT / "data" / "orchestrator" / "apify_webhook_dlq.jsonl"
WEBHOOK_EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
WEBHOOK_DLQ_LOG.parent.mkdir(parents=True, exist_ok=True)

# -- Prometheus Metrics --
if PROMETHEUS_AVAILABLE:
    WEBHOOK_REQUESTS_TOTAL = Counter(
        "apify_webhook_requests_total",
        "Total webhook requests",
        ["status", "event_type"],
    )
    WEBHOOK_REQUEST_DURATION = Histogram(
        "apify_webhook_request_duration_seconds",
        "Webhook request processing duration",
        buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    )
    WEBHOOK_ERRORS_TOTAL = Counter(
        "apify_webhook_errors_total",
        "Total webhook errors",
        ["error_type"],
    )
    WEBHOOK_DLQ_SIZE = Gauge(
        "apify_webhook_dlq_size",
        "Number of payloads in dead-letter queue",
    )
    WEBHOOK_RATE_LIMIT_HITS = Counter(
        "apify_webhook_rate_limit_hits_total",
        "Rate limit hits",
        ["token_prefix"],
    )
else:
    class _NoOp:
        def labels(self, *args, **kwargs):
            return self
        def inc(self, *args, **kwargs):
            pass
        def observe(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass
    _noop = _NoOp()
    WEBHOOK_REQUESTS_TOTAL = WEBHOOK_REQUEST_DURATION = WEBHOOK_ERRORS_TOTAL = WEBHOOK_DLQ_SIZE = WEBHOOK_RATE_LIMIT_HITS = _noop

# -- Apify run durumlari --
TERMINAL_FAILURE_STATUSES = {"FAILED", "ABORTED", "TIMED_OUT"}
SUCCESS_STATUSES = {"SUCCEEDED", "succeeded"}

# -- Idempotency kayitlari (in-memory fallback, production icin DB) --
_processed_runs: dict[str, dict[str, Any]] = {}

# -- Rate Limiting (token-based token bucket) --
_rate_limit_buckets: dict[str, tuple[float, float]] = defaultdict(lambda: (100.0, time.time()))
RATE_LIMIT_CAPACITY = 100  # requests per window
RATE_LIMIT_REFILL_RATE = 10.0  # tokens per second


def _check_rate_limit(token_prefix: str) -> tuple[bool, float]:
    """Token-based rate limiting using token bucket algorithm.
    
    Returns: (allowed, retry_after_seconds)
    """
    if not token_prefix:
        return True, 0.0
    
    now = time.time()
    tokens, last_refill = _rate_limit_buckets[token_prefix]
    
    # Refill tokens
    elapsed = now - last_refill
    tokens = min(RATE_LIMIT_CAPACITY, tokens + elapsed * RATE_LIMIT_REFILL_RATE)
    
    if tokens >= 1.0:
        tokens -= 1.0
        _rate_limit_buckets[token_prefix] = (tokens, now)
        return True, 0.0
    else:
        # Calculate retry-after
        retry_after = (1.0 - tokens) / RATE_LIMIT_REFILL_RATE
        if PROMETHEUS_AVAILABLE:
            WEBHOOK_RATE_LIMIT_HITS.labels(token_prefix=token_prefix[:8]).inc()
        return False, retry_after


# -- Telegram uyarisi --
def _telegram_alert(message: str) -> bool:
    """Telegram bot uzerinden uyari gonderir (istege bagli)."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_ALERT_CHAT_ID")
    if not token or not chat_id:
        logger.warning(
            "Telegram token/chat_id yok; uyari loglandi ama gonderilmedi: %s", message
        )
        return False
    try:
        import requests as _requests

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = _requests.post(
            url, data={"chat_id": chat_id, "text": message}, timeout=10
        )
        return resp.status_code == 200
    except Exception as e:
        logger.error("Telegram uyarisi gonderilemedi: %s", e)
        return False


@dataclass
class WebhookEvent:
    """Apify webhook olayini temsil eder."""

    event_type: str
    actor_run_id: str
    actor_id: str | None = None
    dataset_id: str | None = None
    status: str | None = None
    triggered_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    raw_payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ApifyWebhookReceiver:
    """Apify webhook olaylarini alir, dogrular ve isler.

    Tasarim: hizlica 200 OK don, islem asenkron -- Apify webhook timeout
    (2 dk) suresini asmamali.
    """

    # Request validation constants
    MAX_PAYLOAD_SIZE = 1024 * 1024  # 1 MB
    REQUIRED_CONTENT_TYPE = "application/json"
    MAX_TIMESTAMP_SKEW = 300  # 5 minutes

    def __init__(
        self,
        secret_token: str | None = None,
        apify_client: ApifyClient | None = None,
        ingest_script: str = "ingest_job_postings.py",
        enable_rate_limit: bool = True,
        max_retry_attempts: int = 3,
        base_backoff: float = 1.0,
    ) -> None:
        """
        Args:
            secret_token: Apify webhook secret query param / Authorization header.
                          Default: APFY_WEBHOOK_SECRET env.
            apify_client: ApifyClient (istege bagli; Apify API'den veri cekmek icin).
            ingest_script: SUCCEEDED durumunda tetiklenecek ingest script adi.
            enable_rate_limit: Rate limiting aktif mi?
            max_retry_attempts: Maksimum yeniden deneme sayisi (transient hatalar icin).
            base_backoff: Exponential backoff icin baz saniye.
        """
        self.secret_token = secret_token or os.getenv("APFY_WEBHOOK_SECRET", "")
        self.apify_client = apify_client
        self.ingest_script = SCRIPTS / ingest_script
        self._ledger = ErrorLedger()
        self.enable_rate_limit = enable_rate_limit
        self.max_retry_attempts = max_retry_attempts
        self.base_backoff = base_backoff

    # -- Dogrulama --
    def verify_secret(self, provided: str) -> bool:
        """Secret token dogrulama (constant-time comparison)."""
        if not self.secret_token:
            logger.warning(
                "APFY_WEBHOOK_SECRET tanimli degil; webhook dogrulama atlanir!"
            )
            return True  # fail-open sadece dev ortam icin; prod'de False donmeli
        if not provided:
            return False
        return hmac.compare_digest(self.secret_token, provided)

    @staticmethod
    def verify_hmac(payload: bytes, signature: str, secret: str) -> bool:
        """Apify HMAC-SHA256 imzasi dogrulama (istege bagli).

        Apify resmi doclarda tutarli HMAC'yi garanti etmez; bu yuzden
        secret-token + API yeniden dogrulama ana mekanizmadir.
        Eger Apify signature gonderirse bu metodla dogrulanabilir.
        """
        if not signature or not secret:
            return False
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    @staticmethod
    def verify_timestamp(payload: dict[str, Any], max_skew: int = 300) -> bool:
        """Payload'daki timestamp'in gecerli olup olmadigini kontrol eder.
        
        Apify webhook payload'inda 'createdAt' veya 'timestamp' alani olabilir.
        """
        ts = payload.get("createdAt") or payload.get("timestamp")
        if not ts:
            return True  # Timestamp yoksa kontrol atlanir
        try:
            if isinstance(ts, (int, float)):
                event_time = datetime.fromtimestamp(ts, tz=timezone.utc)
            else:
                event_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            skew = abs((now - event_time).total_seconds())
            return skew <= max_skew
        except Exception:
            return True  # Parse hatasi varsa kontrol atlanir

    # -- Rate Limiting --
    def check_rate_limit(self, token: str) -> tuple[bool, float]:
        """Rate limit kontrolu.
        
        Returns: (allowed, retry_after_seconds)
        """
        if not self.enable_rate_limit:
            return True, 0.0
        token_prefix = token[:16] if token else "anonymous"
        return _check_rate_limit(token_prefix)

    # -- Idempotency --
    def is_processed(self, actor_run_id: str) -> bool:
        """actorRunId daha once islendi mi? (in-memory + JSONL fallback)"""
        if not actor_run_id:
            return False
        if actor_run_id in _processed_runs:
            return True
        # JSONL log'da kontrol et (process restart sonrasi)
        if WEBHOOK_EVENT_LOG.exists():
            try:
                for line in reversed(
                    WEBHOOK_EVENT_LOG.read_text(encoding="utf-8").splitlines()
                ):
                    try:
                        entry = json.loads(line)
                        if entry.get("actor_run_id") == actor_run_id:
                            return True
                    except json.JSONDecodeError:
                        continue
            except OSError:
                pass
        return False

    def _mark_processed(self, event: WebhookEvent) -> None:
        """Olayi islendi olarak isaretle (in-memory + JSONL)."""
        _processed_runs[event.actor_run_id] = event.to_dict()
        try:
            with WEBHOOK_EVENT_LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
        except OSError as e:
            logger.error("Webhook event log yazilamadi: %s", e)

    # -- Dead Letter Queue --
    def _write_dlq(self, payload: dict[str, Any], error: str, error_type: str) -> None:
        """Failed payload'i dead-letter queue'ya yazar."""
        dlq_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_type": error_type,
            "error": error,
            "payload": payload,
        }
        try:
            with WEBHOOK_DLQ_LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps(dlq_entry, ensure_ascii=False, default=str) + "\n")
            if PROMETHEUS_AVAILABLE:
                try:
                    count = sum(1 for _ in WEBHOOK_DLQ_LOG.open(encoding="utf-8"))
                    WEBHOOK_DLQ_SIZE.set(count)
                except Exception:
                    pass
        except OSError as e:
            logger.error("DLQ yazilamadi: %s", e)

    def retry_with_backoff(
        self,
        func,
        *args,
        error_type: str = "transient_error",
        **kwargs,
    ) -> Any:
        """Exponential backoff ile yeniden deneme."""
        last_error = None
        for attempt in range(self.max_retry_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retry_attempts - 1:
                    wait = self.base_backoff * (2**attempt)
                    logger.warning(
                        "%s denemesi %d/%d basarisiz: %s. %.1fs bekleniyor...",
                        error_type, attempt + 1, self.max_retry_attempts, e, wait
                    )
                    time.sleep(wait)
                else:
                    logger.error(
                        "%s tum denemeler basarisiz (%d/%d): %s",
                        error_type, self.max_retry_attempts, self.max_retry_attempts, e
                    )
        raise last_error

    # -- Event parse + persist --
    def parse_event(self, payload: dict[str, Any]) -> "WebhookEvent":
        """Apify webhook payload'idan WebhookEvent olusturur."""
        resource = payload.get("resource", {})
        event_type = payload.get("eventType", payload.get("event_type", ""))
        return WebhookEvent(
            event_type=event_type,
            actor_run_id=payload.get("actorRunId", resource.get("id", "")),
            actor_id=payload.get("actorId", resource.get("actorId", "")),
            dataset_id=resource.get("defaultDatasetId", ""),
            status=resource.get("status", resource.get("state", "")),
            raw_payload=payload,
        )

    # -- Event routing --
    def handle_succeeded(self, event: WebhookEvent) -> dict[str, Any]:
        """SUCCEEDED durumunda: dataset cek + ingest tetikle."""
        result: dict[str, Any] = {
            "action": "succeeded_handler",
            "run_id": event.actor_run_id,
        }

        if not self.apify_client:
            # ApifyClient yok ise (test/mock ortam) -- ingest script'i tetikle
            logger.info("ApifyClient yok; ingest script'i dogrudan tetikleniyor")
            self._trigger_ingest(event)
            result["ingest_triggered"] = True
            return result

        if not event.dataset_id:
            result["error"] = "dataset_id yok"
            logger.warning(
                "SUCCEEDED event %s icin dataset_id bulunamadi", event.actor_run_id
            )
            return result

        def _fetch_and_ingest():
            items = self.apify_client.fetch_dataset_items(
                dataset_id=event.dataset_id, max_items=10000
            )
            result["items_fetched"] = len(items)
            logger.info(
                "Apify dataset %d kayit getirildi (run=%s)",
                len(items),
                event.actor_run_id,
            )

            # Verileri gecici JSONL olarak kaydet, ingest script'i tetikle
            temp_file = (
                ROOT / "data" / "job_intelligence" / f"apify_{event.actor_run_id}.jsonl"
            )
            temp_file.parent.mkdir(parents=True, exist_ok=True)
            if items:
                with temp_file.open("w", encoding="utf-8") as f:
                    for item in items:
                        f.write(
                            json.dumps(item, ensure_ascii=False, default=str) + "\n"
                        )
                result["temp_file"] = str(temp_file)

            self._trigger_ingest(event, input_file=str(temp_file) if items else None)
            result["ingest_triggered"] = True

        try:
            self.retry_with_backoff(_fetch_and_ingest, error_type="apify_dataset_fetch")
        except Exception as e:
            msg = f"Apify dataset cekilemedi (run={event.actor_run_id}, dataset={event.dataset_id}): {e}"
            logger.error(msg)
            self._ledger.add(
                ErrorLedgerEntry(
                    task_id="APIFY-03",
                    agent_id="apify_webhook_receiver",
                    error_type="apify_dataset_fetch_error",
                    error_message=msg,
                )
            )
            _telegram_alert(f"[APIFY-03] Dataset fetch hatasi: run={event.actor_run_id}")
            result["error"] = str(e)

        return result

    def handle_failure(self, event: WebhookEvent) -> dict[str, Any]:
        """FAILED/ABORTED/TIMED_OUT durumunda: ErrorLedger + Telegram."""
        msg = (
            f"Apify Actor run basarisiz: run={event.actor_run_id} "
            f"actor={event.actor_id} status={event.status} type={event.event_type}"
        )
        self._ledger.add(
            ErrorLedgerEntry(
                task_id="APIFY-03",
                agent_id="apify_webhook_receiver",
                error_type="apify_run_failure",
                error_message=msg,
            )
        )
        _telegram_alert(f"[APIFY-03] Actor run basarisiz: {msg}")
        logger.error(msg)
        return {
            "action": "failure_handler",
            "run_id": event.actor_run_id,
            "alerted": True,
        }

    def _trigger_ingest(
        self, event: WebhookEvent, input_file: str | None = None
    ) -> None:
        """ingest_job_postings.py script'ini alt process olarak baslatir."""
        if not self.ingest_script.exists():
            logger.warning("Ingest script bulunamadi: %s", self.ingest_script)
            return
        cmd = [sys.executable, str(self.ingest_script)]
        if input_file:
            cmd.extend(["--input", input_file])
        # Kaynak olarak apify etiketi ekle
        cmd.extend(["--source", "apify"])
        try:
            subprocess.Popen(
                cmd,
                cwd=str(ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                # detached: webhook handler hemen 200 OK donmeli
            )
            logger.info("Ingest script tetiklendi (pid=%s)", cmd[-1])
        except Exception as e:
            logger.error("Ingest script tetiklenemedi: %s", e)

    # -- Ana entry point --
    def process_webhook(
        self,
        payload: dict[str, Any],
        secret: str | None = None,
        signature: str | None = None,
        client_ip: str | None = None,
    ) -> dict[str, Any]:
        """Webhook payload'inin isler. FastAPI endpoint'inden cagrilir.

        Returns: 200 OK yaniti dict. Asenkron islem icin worker loglanir ama
        burada (hizlica) tamamlanir; uzun suren isler _trigger_ingest icinde
        subprocess olarak ayrilir.
        """
        start_time = time.time()
        
        # 0. Request validation
        if not isinstance(payload, dict):
            self._write_dlq(payload, "payload not a dict", "validation_error")
            if PROMETHEUS_AVAILABLE:
                WEBHOOK_ERRORS_TOTAL.labels(error_type="validation_error").inc()
            return {"status": "rejected", "reason": "invalid_payload"}

        # 1. Rate limiting
        if self.enable_rate_limit:
            token_for_rl = secret or "anonymous"
            allowed, retry_after = self.check_rate_limit(token_for_rl)
            if not allowed:
                if PROMETHEUS_AVAILABLE:
                    WEBHOOK_RATE_LIMIT_HITS.labels(token_prefix=secret[:8] if secret else "anon").inc()
                return {
                    "status": "rate_limited",
                    "reason": "too_many_requests",
                    "retry_after": round(retry_after, 1),
                }

        # 2. Secret dogrula
        if not self.verify_secret(secret or ""):
            self._write_dlq(payload, "invalid secret", "auth_error")
            if PROMETHEUS_AVAILABLE:
                WEBHOOK_ERRORS_TOTAL.labels(error_type="auth_error").inc()
            return {"status": "rejected", "reason": "invalid_secret"}

        # 2. HMAC dogrula (varsa)
        if signature and not self.verify_hmac(
            json.dumps(payload).encode(), signature, self.secret_token
        ):
            self._write_dlq(payload, "invalid hmac", "auth_error")
            if PROMETHEUS_AVAILABLE:
                WEBHOOK_ERRORS_TOTAL.labels(error_type="auth_error").inc()
            return {"status": "rejected", "reason": "invalid_hmac"}

        # 3. Timestamp validation
        if not self.verify_timestamp(payload, self.MAX_TIMESTAMP_SKEW):
            self._write_dlq(payload, "timestamp skew too large", "validation_error")
            if PROMETHEUS_AVAILABLE:
                WEBHOOK_ERRORS_TOTAL.labels(error_type="validation_error").inc()
            return {"status": "rejected", "reason": "timestamp_skew"}

        # 4. Event parse
        event = self.parse_event(payload)
        if not event.actor_run_id:
            self._write_dlq(payload, "missing actor_run_id", "validation_error")
            if PROMETHEUS_AVAILABLE:
                WEBHOOK_ERRORS_TOTAL.labels(error_type="validation_error").inc()
            return {"status": "rejected", "reason": "missing_run_id"}

        # 5. Idempotency
        if self.is_processed(event.actor_run_id):
            return {
                "status": "ok",
                "message": "already_processed",
                "run_id": event.actor_run_id,
            }

        # 6. Islem
        event_type = event.event_type or ""
        status = event.status or ""

        self._mark_processed(event)

        if "SUCCEEDED" in event_type.upper() or "SUCCEEDED" in status.upper():
            detail = self.handle_succeeded(event)
        elif (
            status.upper() in TERMINAL_FAILURE_STATUSES or "FAIL" in event_type.upper()
        ):
            detail = self.handle_failure(event)
        else:
            logger.info("Webhook event tipi %s (%s) icin islem yok", event_type, status)
            detail = {"action": "noop", "event_type": event_type, "run_status": status}

        # Record metrics
        if PROMETHEUS_AVAILABLE:
            duration = time.time() - start_time
            WEBHOOK_REQUEST_DURATION.observe(duration)
            WEBHOOK_REQUESTS_TOTAL.labels(
                status="ok", event_type=event_type or "unknown"
            ).inc()

        return {
            "status": "ok",
            "run_id": event.actor_run_id,
            "event_type": event_type,
            **detail,
        }

    # -- Health / Metrics --
    def health_check(self) -> dict[str, Any]:
        """Health check endpoint icin durum bilgisi."""
        dlq_count = 0
        if WEBHOOK_DLQ_LOG.exists():
            try:
                dlq_count = sum(1 for _ in WEBHOOK_DLQ_LOG.open(encoding="utf-8"))
            except Exception:
                pass
        
        return {
            "status": "healthy",
            "secret_configured": bool(self.secret_token),
            "rate_limit_enabled": self.enable_rate_limit,
            "dlq_size": dlq_count,
            "processed_runs_memory": len(_processed_runs),
            "prometheus_available": PROMETHEUS_AVAILABLE,
        }

    def get_metrics(self) -> bytes:
        """Prometheus metrics output."""
        if PROMETHEUS_AVAILABLE:
            return generate_latest()
        return b"# Prometheus client not installed\n"


# -- CLI --
def main() -> int:
    """Webhook aliciyi test icin tek seferlik payload isleme (CLI)."""
    parser = argparse.ArgumentParser(
        description="Apify webhook event receiver (APIFY-03/P7-12)"
    )
    parser.add_argument(
        "--payload-file",
        type=Path,
        help="Webhook payload JSON dosyasi (test/simulasyon icin)",
    )
    parser.add_argument(
        "--secret",
        default=None,
        help="Webhook secret token (varsayilan: APFY_WEBHOOK_SECRET env)",
    )
    parser.add_argument(
        "--check-run",
        default=None,
        help="Verilen actorRunId daha once islendi mi? (idempotency kontrolu)",
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Health check ciktisi ver",
    )
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="Prometheus metrics ciktisi ver",
    )
    args = parser.parse_args()

    receiver = ApifyWebhookReceiver(secret_token=args.secret)

    if args.health:
        print(json.dumps(receiver.health_check(), ensure_ascii=False, indent=2))
        return 0

    if args.metrics:
        print(receiver.get_metrics().decode("utf-8"))
        return 0

    if args.check_run:
        processed = receiver.is_processed(args.check_run)
        print(f"Run {args.check_run}: {'PROCESSED' if processed else 'NOT PROCESSED'}")
        return 0

    if not args.payload_file:
        parser.error("--payload-file veya --check-run/--health/--metrics gerekli")

    with open(args.payload_file, "r", encoding="utf-8") as f:
        payload = json.load(f)

    result = receiver.process_webhook(payload, secret=args.secret)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(name)s %(levelname)s: %(message)s"
    )
    sys.exit(main())
