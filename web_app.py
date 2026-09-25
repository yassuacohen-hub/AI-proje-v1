#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""FastAPI backend - Company Master Web Dashboard API (SQLite-uyumlu)."""

from __future__ import annotations

import asyncio
import json
import os
import uuid
import sys
import time
try:  # Python 3.11+ standart kutuphane
    import tomllib
except ModuleNotFoundError:  # Python 3.10: harici tomli paketi
    import tomli as tomllib  # type: ignore[no-redef]
from datetime import datetime
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

import pyotp
import qrcode
import base64
from io import BytesIO

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine
from company_master.intelligence.job_intelligence.api.router import (
    router as job_intelligence_router,
)
from company_master.orchestrator import task_board as tb  # noqa: E402
from scripts.apify_webhook_receiver import ApifyWebhookReceiver  # noqa: E402
from src.company_master.admin.caching import admin_cache

# DASH-01 Phase 1: Auth & RBAC infrastructure (S-1/S-2/S-3)
from company_master.auth.session import (
    get_session as _get_session,
    require_auth as _require_auth,
    SESSION_COOKIE_NAME as _SESSION_COOKIE_NAME,
)
from company_master.auth.rbac import (
    has_role as _has_role,
    ROLE_ADMIN as _ROLE_ADMIN,
    ROLE_USER as _ROLE_USER,
)

# OpenTelemetry tracing
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

# Query profiler
import time as _perf_time

_DB_TIME_MS = 0.0
_CACHE_HITS = 0
_CACHE_MISSES = 0
_QUERY_COUNT = 0
_QUERY_TIMES = []

# API-SPLIT-01: normalize module
from src.company_master.api.core.normalize import (
    _tr_insensitive, _tr_rx_key, _tr_rx, _tr_rx_soft_end,
    _clean_double_dots, _mask_email, _mask_phone, apply_kvkk_mask, _mask_active,
    normalize_company_name, extract_trade_name, normalize_company, tr_normalize,
)


def _profile_query(name, fn):
    global _DB_TIME_MS, _QUERY_COUNT
    start = _perf_time.perf_counter()
    result = fn()
    elapsed_ms = (_perf_time.perf_counter() - start) * 1000
    _DB_TIME_MS += elapsed_ms
    _QUERY_COUNT += 1
    _QUERY_TIMES.append({"name": name, "ms": round(elapsed_ms, 2)})
    return result


# â”€â”€ ANA KURAL: Firma ad normalizasyonu (V10/09_kurallar_ve_promptlar/11_unvan_kisaltma_ve_tabela_kurallari) â”€â”€
# Kural 1: Firma adlari her zaman BUYUK HARFLE yazilir
# Kural 2: Uzun ifadeler standart kisaltilir (SANAYİ VE TİCARET â†’ SAN. VE TİC.)
# Kural 3: Tabela ismi = ilgi alanı/marka (ilk 2-3 kelime, VE/Şirket Turu/Faaliyet filtrelenerek)

import re as _re

# Turkce duyarsiz eslesme: kural 2 kisaltmalari ASCII tanimli; girdideki
# Turkce harfler (I noktali/ciftesleri) de eslesmeli.
_TR_INSENSITIVE_CLS = {
    "I": "[İI]",
    "C": "[ÇC]",
    "G": "[ĞG]",
    "O": "[ÖO]",
    "U": "[ÜU]",
    "S": "[ŞS]",
}



# Dashboard performance counters

app = FastAPI(title="Company Master Dashboard API", version="1.0")
if OTEL_AVAILABLE:
    # Set up tracer provider
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    # Configure Jaeger exporter (optional, can be configured via env)
    jaeger_host = os.getenv("JAEGER_HOST", "localhost")
    jaeger_port = int(os.getenv("JAEGER_PORT", "6831"))
    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_host,
        agent_port=jaeger_port,
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    # Instrument requests library (for outbound HTTP calls)
    RequestsInstrumentor().instrument()

# â”€â”€ API Key Auth & Rate Limiting (Y6) â”€â”€
# DASH_API_KEY env'de tanimliysa zorunlu, degilse dev modu (herkese acik).
# Frontend dashboard'a ?api_key=KEY ile erisince key otomatik tasinir.
DASH_API_KEY = os.getenv("DASH_API_KEY", "").strip()
_auth_banner = (
    "API key zorunlu degil (dev modu)" if not DASH_API_KEY else "API key korumasi AKTIF"
)

# â”€â”€ KVKK PII Maskeleme (Y7) â”€â”€
# DASH_MASK_PII=1 ise TUM PII maskelemeli doner (musteri preview modu).
# Endpoint bazinda ?mask=1 ile istek bazli da acilabilir (env'den bagimsiz).
DASH_MASK_PII = os.getenv("DASH_MASK_PII", "0").strip() == "1"

# Basit in-memory rate limit: ip -> [tick, sayac]
_RATE_LIMIT: dict[str, list] = {}
_RATE_LIMIT_MAX = int(os.getenv("DASH_RATE_LIMIT_MAX", "120"))  # istek / dakika
_RATE_LIMIT_WINDOW = 60
# SEC-AUTH-01 Y-1: auth uçları için ayrı, katı IP limiti (brute-force yavaşlatma).
_AUTH_RATE_LIMIT: dict[str, list] = {}
_AUTH_RATE_LIMIT_MAX = int(os.getenv("AUTH_RATE_LIMIT_MAX", "5"))  # istek / dakika

# Y26: API key kullanim metrikleri (tier bazli istek sayaci, in-memory)
_API_USAGE: dict[str, dict[str, int]] = {}  # tier -> endpoint -> sayac
_TIER_RATE_LIMITS = {"terminal": 60, "strategic": 120, "enterprise": 600}  # istek/dk


def _record_api_usage(tier: str, path: str) -> None:
    """Tier bazli istek sayaci (/metrics raporu icin)."""
    entry = _API_USAGE.setdefault(tier, {})
    entry[path] = entry.get(path, 0) + 1


def api_usage_snapshot() -> dict:
    """Kopya dondurur (metrik endpoint'i icin)."""
    return {t: dict(v) for t, v in _API_USAGE.items()}


def _user_from_api_key(api_key: str):
    """Y26: API key ile kullaniyi bulur (enterprise tier kontrolu icin)."""
    if not api_key or not api_key.startswith("ent_"):
        return None
    try:
        engine = get_engine()
        with engine.connect() as conn:
            row = (
                conn.execute(
                    text(
                        "SELECT user_id, email, role, status, tier, api_key FROM users "
                        "WHERE api_key = :k"
                    ),
                    {"k": api_key},
                )
                .mappings()
                .first()
            )
        return dict(row) if row else None
    except Exception:
        return None


def require_api_key(request: Request) -> str:
    """Endpoint'lere dependency olarak eklenir:
        def endpoint(api_key: str = Depends(require_api_key)):
    Y26: gecen key enterprise uye key'i ise tier bazli sayac + yuksek rate limit uygulanir.
    """
    # 1) Session kontrolü: HttpOnly çerezden SessionUser al
    session = _get_session(request)
    if session and session.user:
        # Session bazlı auth: kullanıcı rolüne ve kredisine göre erişim
        user = session.user
        tier = user.tier if user.tier else "public"
    else:
        # 2) Fallback: API key kontrolü (X-API-Key header veya ?api_key= query param)
        # HttpOnly çerezden API key'ini de al (session.py'den)
        key = request.cookies.get("huginn_api_key", "")
        if not key:
            key = request.headers.get("X-API-Key", "") or request.query_params.get(
                "api_key", ""
            )

        tier = "public"

        if key:
            u = _user_from_api_key(key)
            if u and u.get("api_key") == key and u.get("tier") == "enterprise":
                tier = "enterprise"
            elif key == DASH_API_KEY:
                tier = "public"
            elif not u:
                raise HTTPException(
                    status_code=401,
                    detail="Gecersiz API key. X-API-Key header veya huginn_api_key cookie gerekli.",
                )
        elif DASH_API_KEY:
            raise HTTPException(
                status_code=401,
                detail="API key zorunlu. X-API-Key header veya huginn_api_key cookie gerekli.",
            )

    # 3) Rate limiting (tier bazli; her IP icin 1 dakikalik pencere)
    limit = _TIER_RATE_LIMITS.get(tier, _RATE_LIMIT_MAX)
    ip = request.client.host if request.client else "local"
    now = time.time()
    entry = _RATE_LIMIT.get(ip)
    if not entry or now - entry[0] > _RATE_LIMIT_WINDOW:
        _RATE_LIMIT[ip] = [now, 1]
    else:
        entry[1] += 1
        if entry[1] > max(limit, _RATE_LIMIT_MAX):
            raise HTTPException(
                status_code=429, detail="Cok fazla istek. Lutfen biraz bekleyin."
            )

    if tier == "enterprise":
        _record_api_usage(tier, request.url.path)

    # Return the effective key for endpoint usage
    if session and session.user:
        return session.user.user_id or "session-auth"
    return key or "public"


def require_api_key_optional(request: Request) -> str:
    """Zorunlu olmayan auth (rate limit yine uygulanir) - dashboard HTML icin."""
    return require_api_key(request) if DASH_API_KEY else "public"


def _auth_rate_guard(request: Request) -> None:
    """SEC-AUTH-01 Y-1: auth uçları için IP bazlı katı limit (varsayılan 5/dk).

    `require_api_key`'in genel sayacından bağımsız ayrı kova (_AUTH_RATE_LIMIT)
    tutar; pencere (_RATE_LIMIT_WINDOW) içinde limit aşılırsa 429 döner.
    Login / reset-request / reset-confirm / change-password uçlarına
    `Depends(_auth_rate_guard)` ile bağlanır.
    """
    ip = request.client.host if request.client else "local"
    now = time.time()
    entry = _AUTH_RATE_LIMIT.get(ip)
    if not entry or now - entry[0] > _RATE_LIMIT_WINDOW:
        _AUTH_RATE_LIMIT[ip] = [now, 1]
        return
    entry[1] += 1
    if entry[1] > _AUTH_RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=429, detail="Cok fazla istek. Lutfen biraz bekleyin."
        )


_CACHE: dict[str, tuple[float, Any]] = {}

# ADMIN-UI-CACHE-OPT-01: TTL ve boyut siniri env ile ayarlanabilir.
# Varsayilanlar korundu: TTL 300 sn, ust sinir 512 kayit (geriye uyumlu).
_CACHE_TTL_ENV = "HUGINN_CACHE_TTL"
_CACHE_MAX_ENV = "HUGINN_CACHE_MAX_ENTRIES"

# Altyapi marka yazim gecisi (2026-09-23): marka yazimi HUGINN (tek G).
# Asagidaki eski adlar MARKA YAZIMI DEGIL, dis sozlesmedir (kullanicilarin .env
# dosyasinda eski ad yazili olabilir). Bir surum boyunca fallback okunur.
_ESKI_CACHE_ENV = {  # Altyapi marka gecisi: marka adi degil, gecis donemi env takma adi
    _CACHE_TTL_ENV: "HUGGINN_CACHE_TTL",  # marka-muaf: eski env adi (deprecated)
    _CACHE_MAX_ENV: "HUGGINN_CACHE_MAX_ENTRIES",  # marka-muaf: eski env adi (deprecated)
}


def _env_sayi(ad: str, varsayilan: str) -> int:
    """Env degerini int okur; yeni ad bos ise eski (deprecated) adi dener."""
    ham = os.getenv(ad)
    if ham is None:
        eski = _ESKI_CACHE_ENV.get(ad)
        ham = os.getenv(eski) if eski else None
    return int(ham if ham is not None else varsayilan)


_CACHE_TTL = _env_sayi(_CACHE_TTL_ENV, "300")
_CACHE_MAX_ENTRIES = _env_sayi(_CACHE_MAX_ENV, "512")


def _cache_evict_if_needed() -> None:
    """ADMIN-UI-CACHE-OPT-01: cache sinir asiminda en eski kayitlari at."""
    while len(_CACHE) >= _CACHE_MAX_ENTRIES:
        oldest_key = min(_CACHE, key=lambda k: _CACHE[k][0])
        _CACHE.pop(oldest_key, None)


def cache_get(key: str) -> Any | None:
    global _CACHE_HITS, _CACHE_MISSES
    entry = _CACHE.get(key)
    if entry and time.time() - entry[0] < _CACHE_TTL:
        _CACHE_HITS += 1
        return entry[1]
    _CACHE_MISSES += 1
    _CACHE.pop(key, None)
    return None


def cache_set(key: str, value: Any) -> None:
    # ADMIN-UI-CACHE-OPT-01: bos sonuc negatif cache'lenmesin —
    # bos sayfa/arama sonucları TTL boyunca bos kalmasin.
    if isinstance(value, dict) and not value:
        return
    if isinstance(value, (list, tuple)) and len(value) == 0:
        return
    _cache_evict_if_needed()
    _CACHE[key] = (time.time(), value)


ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8501"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)

WEB_DIR = ROOT / "web_dashboard"
WEB_DIR.mkdir(parents=True, exist_ok=True)

app.include_router(job_intelligence_router)
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="web-static")


_apify_webhook_receiver: ApifyWebhookReceiver | None = None


def get_apify_webhook_receiver() -> ApifyWebhookReceiver:
    global _apify_webhook_receiver
    if _apify_webhook_receiver is None:
        _apify_webhook_receiver = ApifyWebhookReceiver()
    return _apify_webhook_receiver


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "time": datetime.now().isoformat()}


@app.post("/api/webhooks/apify")
async def apify_webhook(
    request: Request,
    secret: str | None = None,
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_apify_signature: str | None = Header(default=None, alias="X-Apify-Signature"),
) -> dict:
    """APIFY-03/P7-12: Hardened Apify webhook alıcı.

    Apify bir Actor run tamamlandığında (veya başarısız olduğunda) bu
    endpoint'e POST gönderir. Hızlıca 200 OK döner; işlem subprocess
    olarak asenkron başlatılır.

    Prod Hardening (P7-12):
    - Rate limiting per token (token bucket)
    - Dead-letter queue (DLQ) for failed payloads
    - Retry/backoff with exponential backoff for transient failures
    - Request validation (size limits, content-type, timestamp)
    - Prometheus metrics
    - Idempotency via actorRunId

    Auth: ?secret= token veya Authorization: Bearer header.
    """
    receiver = get_apify_webhook_receiver()

    # Content-Type validation
    content_type = request.headers.get("content-type", "")
    if not content_type.startswith("application/json"):
        raise HTTPException(
            status_code=415,
            detail="Content-Type must be application/json",
        )

    # Payload size limit (1MB)
    body = await request.body()
    if len(body) > receiver.MAX_PAYLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Payload too large (max {receiver.MAX_PAYLOAD_SIZE} bytes)",
        )

    # Parse JSON
    try:
        payload = json.loads(body) if body else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        receiver._write_dlq({"raw_body": body.decode("utf-8", errors="replace")}, "invalid_json", "validation_error")
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload",
        )

    # Secret: query param > Authorization Bearer
    provided_secret = secret or ""
    if not provided_secret and authorization:
        provided_secret = authorization.replace("Bearer ", "").strip()

    # HMAC verification (optional - Apify signature)
    if x_apify_signature:
        if not receiver.verify_hmac(body, x_apify_signature, receiver.secret_token):
            receiver._write_dlq(payload, "invalid hmac", "auth_error")
            raise HTTPException(
                status_code=401,
                detail="Invalid HMAC signature",
            )

    # Process webhook through hardened receiver
    client_ip = request.client.host if request.client else "unknown"
    result = receiver.process_webhook(
        payload,
        secret=provided_secret,
        signature=x_apify_signature or "",
        client_ip=client_ip,
    )

    # Handle rate limiting with Retry-After header
    if result.get("status") == "rate_limited":
        retry_after = result.get("retry_after", 1.0)
        raise HTTPException(
            status_code=429,
            detail=result.get("reason", "Rate limit exceeded"),
            headers={"Retry-After": str(int(retry_after) + 1)},
        )

    # Handle auth/rejection errors
    if result.get("status") in ("rejected", "unauthorized"):
        raise HTTPException(
            status_code=401,
            detail=result.get("reason", "Unauthorized"),
        )

    return result


@app.get("/api/webhooks/apify/health")
def apify_webhook_health() -> dict:
    """Apify webhook health check endpoint (readiness/liveness).

    Returns:
        - status: healthy/degraded
        - secret_configured: bool
        - rate_limit_enabled: bool
        - dlq_size: int (number of failed payloads in DLQ)
        - processed_runs_memory: int (in-memory idempotency cache size)
        - prometheus_available: bool
    """
    receiver = get_apify_webhook_receiver()
    return receiver.health_check()


@app.get("/api/webhooks/apify/metrics")
def apify_webhook_metrics() -> Response:
    """Prometheus metrics endpoint for Apify webhook.

    Exposes:
        - apify_webhook_requests_total{status,event_type}
        - apify_webhook_request_duration_seconds
        - apify_webhook_errors_total{error_type}
        - apify_webhook_dlq_size
        - apify_webhook_rate_limit_hits_total{token_prefix}
    """
    receiver = get_apify_webhook_receiver()
    metrics_bytes = receiver.get_metrics()
    return Response(
        content=metrics_bytes,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


# ============================================================================
# D-216: TELEGRAM WEBHOOK ENDPOINT
# ============================================================================

@app.post("/api/webhooks/telegram")
async def telegram_webhook(request: Request) -> dict:
    """D-216: Telegram Bot webhook alıcısı.
    
    Telegram Bot API güncellemelerini (message, callback_query vb.) alır,
    telegram_bot.py içindeki handler'lara iletir.
    
    Body (JSON):
        {
            "update_id": int,
            "message": {...} | null,
            "callback_query": {...} | null,
            ...
        }
    
    Returns:
        {"ok": true, "message": "Update processed"}
"""
    import json
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Request body'yi oku
        body = await request.json()
        update_id = body.get("update_id", 0)
        
        logger.info(f"[TG-WEBHOOK] Received update_id={update_id}")
        
        # telegram_bot modülü içine iletişim kur
        # (lokal polling modunda bu endpoint kullanılmaz, fakat production için hazır)
        try:
            from src.company_master.telegram_bot import bot
            
            # Telegram Bot API'nin ilettiği update'i bot'a işlet
            bot.process_new_updates([body])
            logger.info(f"[TG-WEBHOOK] Processed update_id={update_id}")
            
        except ImportError:
            logger.warning("[TG-WEBHOOK] telegram_bot module not available (polling mode)")
            # Polling modunda webhook'a POST gelmez, sorun yok
            pass
        
        return {
            "ok": True,
            "message": "Update processed",
            "update_id": update_id,
            "timestamp": datetime.now().isoformat(),
        }
    
    except json.JSONDecodeError as e:
        logger.error(f"[TG-WEBHOOK] JSON decode error: {e}")
        return {"ok": False, "error": "Invalid JSON"}
    
    except Exception as e:
        logger.error(f"[TG-WEBHOOK] Unhandled error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


@app.get("/api/webhooks/telegram/health")
def telegram_webhook_health() -> dict:
    """Telegram webhook health check.
    
    Returns:
        - status: "healthy" veya "degraded"
        - bot_token_configured: bool
        - polling_mode: bool (True ise webhook kullanılmıyor)
    """
    try:
        from src.company_master.telegram_bot import bot, TOKEN
        
        return {
            "status": "healthy",
            "bot_token_configured": bool(TOKEN),
            "polling_mode": True,  # MVP Faz 1 polling kullanıyor
            "endpoint": "/api/webhooks/telegram",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/metrics")
def metrics() -> dict:
    """Prometheus formatinda metrik verisi - tek sorgu optimize."""
    global _CACHE_HITS, _CACHE_MISSES
    import json, hashlib

    cache_key = hashlib.md5(b"metrics:v1").hexdigest()
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT COUNT(*) as total,
                   AVG(data_quality_score) as avg_score,
                   SUM(CASE WHEN tax_number IS NOT NULL AND tax_number != '' THEN 1 ELSE 0 END) as with_tax,
                   SUM(CASE WHEN website_domain IS NOT NULL AND website_domain != '' THEN 1 ELSE 0 END) as with_web,
                   SUM(CASE WHEN nace_code IS NOT NULL AND nace_code != '' THEN 1 ELSE 0 END) as with_nace,
                   SUM(CASE WHEN primary_phone IS NOT NULL AND primary_phone != '' THEN 1 ELSE 0 END) as with_phone,
                   SUM(CASE WHEN primary_email IS NOT NULL AND primary_email != '' THEN 1 ELSE 0 END) as with_email,
                   SUM(CASE WHEN osb_parsel IS NOT NULL AND osb_parsel != '' THEN 1 ELSE 0 END) as with_parsel,
                   SUM(CASE WHEN adres IS NOT NULL AND adres != '' THEN 1 ELSE 0 END) as with_adres
            FROM companies
            WHERE is_ankara=TRUE
        """)).mappings().first()
        if not r:
            return {}
        _db_elapsed = (_perf_time.perf_counter() - _q_start) * 1000
        global _DB_TIME_MS
        _DB_TIME_MS += _db_elapsed
        return {
            "huginn_companies_total": r["total"],
            "huginn_companies_avg_quality_score": round(
                float(r["avg_score"]) if r.get("avg_score") is not None else 0, 2
            ),
            "huginn_companies_with_tax_number": r["with_tax"],
            "huginn_companies_with_website": r["with_web"],
            "huginn_companies_with_nace_code": r["with_nace"],
            "huginn_companies_with_phone": r["with_phone"],
            "huginn_companies_with_email": r["with_email"],
            "huginn_companies_with_osb_parsel": r["with_parsel"],
            "huginn_companies_with_adres": r["with_adres"],
            "huginn_query_count": _QUERY_COUNT,
            "huginn_db_time_ms": round(_DB_TIME_MS, 2),
            "huginn_cache_hits": _CACHE_HITS,
            "huginn_cache_misses": _CACHE_MISSES,
            "huginn_cache_hit_rate": round(
                _CACHE_HITS / max(1, _CACHE_HITS + _CACHE_MISSES), 4
            ),
            "huginn_timestamp": datetime.now().isoformat(),
        }


@admin_cache(ttl=60)
@app.get("/api/kpi")
def api_kpi(_auth: str = Depends(require_api_key)) -> dict:
    # Cache TTL: 60s
    """KPI ozeti - SQLite/PostgreSQL uyumlu (FILTER yerine CASE WHEN)."""
    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT COUNT(*) as total,
                SUM(CASE WHEN c.tax_number IS NOT NULL AND c.tax_number != '' THEN 1 ELSE 0 END) as tax,
                SUM(CASE WHEN c.vergi_no IS NOT NULL AND c.vergi_no != '' THEN 1 ELSE 0 END) as vergi,
                SUM(CASE WHEN COALESCE(c.tax_number, c.vergi_no) IS NOT NULL AND COALESCE(c.tax_number, c.vergi_no) != '' THEN 1 ELSE 0 END) as vkn_either,
                SUM(CASE WHEN c.website_domain IS NOT NULL AND c.website_domain != '' THEN 1 ELSE 0 END) as web,
                SUM(CASE WHEN c.osb_parsel IS NOT NULL AND c.osb_parsel != '' THEN 1 ELSE 0 END) as parsel,
                SUM(CASE WHEN c.adres IS NOT NULL AND c.adres != '' THEN 1 ELSE 0 END) as adres,
                SUM(CASE WHEN c.primary_phone IS NOT NULL AND c.primary_phone != '' THEN 1 ELSE 0 END) as tel,
                SUM(CASE WHEN c.primary_email IS NOT NULL AND c.primary_email != '' THEN 1 ELSE 0 END) as email,
                SUM(CASE WHEN c.nace_code IS NOT NULL AND c.nace_code != '' THEN 1 ELSE 0 END) as nace,
                AVG(c.data_quality_score) as avg_score
            FROM companies c
            WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        """)).mappings().first()
        if r:
            row = dict(r)
            row["avg_score"] = (
                float(row["avg_score"]) if row.get("avg_score") is not None else None
            )
            return row
        return {}


@app.get("/api/kpi/history")
def api_kpi_history(_auth: str = Depends(require_api_key), days: int = 7):
    """Get KPI history for the last N days."""
    if not isinstance(days, int) or days < 1 or days > 30:
        days = 7
    engine = get_engine()
    result = {"days": days, "series": {"login": [], "search": [], "yeni_firma": []}, "labels": []}
    try:
        with engine.connect() as conn:
            labels_sql = text("""
                SELECT DATE('now', '-' || (n-1) || ' day') as date
                FROM (SELECT 1 as n UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION
                      SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION
                      SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15 UNION
                      SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20 UNION
                      SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25 UNION
                      SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29 UNION SELECT 30)
                WHERE n <= :days ORDER BY date DESC
            """)
            try:
                label_rows = conn.execute(labels_sql, {"days": days}).all()
                result["labels"] = [row[0] for row in label_rows]
            except Exception:
                pass
            if not result.get("labels"):
                return result
            login_sql = text("SELECT DATE(login_timestamp) as date, COUNT(*) as cnt FROM login_events WHERE login_timestamp >= datetime(:start_date, 'localtime') GROUP BY DATE(login_timestamp)")
            try:
                login_map = {lbl: 0 for lbl in result["labels"]}
                login_rows = conn.execute(login_sql, {"start_date": result["labels"][-1]}).all()
                for row in login_rows:
                    ds = row[0] if isinstance(row[0], str) else str(row[0])[:10]
                    if ds in login_map: login_map[ds] = row[1] or 0
                result["series"]["login"] = [login_map.get(lbl, 0) for lbl in result["labels"]]
            except Exception:
                pass
            search_sql = text("SELECT DATE(searched_at) as date, COUNT(*) as cnt FROM search_events WHERE searched_at >= datetime(:start_date, 'localtime') GROUP BY DATE(searched_at)")
            try:
                search_map = {lbl: 0 for lbl in result["labels"]}
                search_rows = conn.execute(search_sql, {"start_date": result["labels"][-1]}).all()
                for row in search_rows:
                    ds = row[0] if isinstance(row[0], str) else str(row[0])[:10]
                    if ds in search_map: search_map[ds] = row[1] or 0
                result["series"]["search"] = [search_map.get(lbl, 0) for lbl in result["labels"]]
            except Exception:
                pass
            try:
                firma_sql = text("SELECT DATE(created_at) as date, COUNT(*) as cnt FROM companies WHERE created_at >= datetime(:start_date, 'localtime') GROUP BY DATE(created_at)")
                firma_map = {lbl: 0 for lbl in result["labels"]}
                firma_rows = conn.execute(firma_sql, {"start_date": result["labels"][-1]}).all()
                cumulative = 0
                yf = []
                for row in firma_rows:
                    ds = row[0] if isinstance(row[0], str) else str(row[0])[:10]
                    if ds in firma_map:
                        cumulative += row[1] or 0
                        yf.append(cumulative)
                    else:
                        yf.append(cumulative)
                # Fill to match labels length
                while len(yf) < len(result["labels"]):
                    yf.insert(0, cumulative)
                result["series"]["yeni_firma"] = yf[:len(result["labels"])]
            except Exception:
                result["series"]["yeni_firma"] = [0] * len(result["labels"])
    except Exception:
        pass
    return result

@app.get("/api/tasks")
def api_tasks(_auth: str = Depends(require_api_key)) -> list[dict]:
    board = tb.gorev_listesi()
    return board or []


@app.get("/api/handoffs")
def api_handoffs(_auth: str = Depends(require_api_key)) -> dict:
    return tb.handoff_tum() or {}


MAX_COMPANIES_LIMIT = 500
MAX_SEARCH_LENGTH = 100


@app.get("/api/companies")
def api_companies(
    limit: int = 50,
    offset: int = 0,
    search: str = "",
    min_score: int = 0,
    max_score: int = 100,
    source: str = "",
    sources: str = "",
    nace: str = "",
    mask: int = 0,
    request: Request = None,
    _auth: str = Depends(require_api_key),
) -> dict:
    """Firma listesi - coklu kaynak destegi (sources= virgulle ayrilmis).
    KVKK: mask=1 (veya env DASH_MASK_PII=1) ile telefon/e-posta maskeli doner."""
    limit = min(max(limit, 1), MAX_COMPANIES_LIMIT)
    offset = max(offset, 0)
    search = search.strip()[:MAX_SEARCH_LENGTH]
    min_score = max(0, min(min_score, 100))
    max_score = max(0, min(max_score, 100))

    # Coklu kaynak: sources="ostim.org.tr,aso.org.tr" -> liste
    # Geriye donuk uyum: tek source= parametresi de desteklenir
    source_list = []
    if sources:
        source_list = [s.strip() for s in sources.split(",") if s.strip()]
    elif source:
        source_list = [source.strip()] if source.strip() else []

    # P4-4: cache hit â€” DB roundtrip'i tamamen atlar (TTL 300s)
    # Not: source_list yukarida hesaplandi; mask durumu anahtarda (maskeli/maskesiz ayri).
    import hashlib

    _ck = hashlib.sha256(
        f"companies:{limit}:{offset}:{search}:{min_score}:{max_score}:{source_list}:{nace}:mask={_mask_active(mask)}".encode()
    ).hexdigest()
    _cached = cache_get(_ck)
    if _cached is not None:
        return _cached

    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        where_clauses = ["c.is_ankara=TRUE AND c.is_osb_member=TRUE"]
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "min_score": min_score,
            "max_score": max_score,
        }

        if search:
            # PostgreSQL ILIKE + expression index kullanimi
            # tr_normalize artik sadece fallback; ILIKE trigram/expression index kullanir
            where_clauses.append("""
                (c.legal_name ILIKE :search
                OR c.trade_name ILIKE :search
                OR c.primary_phone ILIKE :search
                OR c.primary_email ILIKE :search
                OR c.tax_number ILIKE :search
                OR c.vergi_no ILIKE :search)
            """)
            params["search"] = f"%{search}%"

        if nace:
            where_clauses.append("c.nace_code LIKE :nace")
            params["nace"] = f"{nace}%"

        # Coklu kaynak filtresi: companies.source_record_id -> source_records.source_id -> sources.source_name
        if source_list:
            if len(source_list) == 1:
                where_clauses.append("""c.source_record_id IN (
                    SELECT sr.source_record_id
                    FROM source_records sr
                    JOIN sources s ON sr.source_id = s.source_id
                    WHERE s.source_name = :source_name
                )""")
                params["source_name"] = source_list[0]
            else:
                # Coklu kaynak: IN (...) ile
                placeholders = []
                for i, src in enumerate(source_list):
                    key = f"src_{i}"
                    placeholders.append(f":{key}")
                    params[key] = src
                where_clauses.append(f"""c.source_record_id IN (
                    SELECT sr.source_record_id
                    FROM source_records sr
                    JOIN sources s ON sr.source_id = s.source_id
                    WHERE s.source_name IN ({", ".join(placeholders)})
                )""")

        where_clauses.append("c.data_quality_score >= :min_score")
        where_clauses.append("c.data_quality_score <= :max_score")

        where_sql = " AND ".join(where_clauses)

        _q_start = _perf_time.perf_counter()
        total = conn.execute(
            text(f"SELECT COUNT(*) FROM companies c WHERE {where_sql}"), params
        ).scalar()
        rows = (
            conn.execute(
                text(f"""
            SELECT c.legal_name, c.trade_name, c.website_domain, c.primary_phone, c.primary_email,
                   c.tax_number, c.vergi_no, c.osb_parsel, c.nace_code, c.data_quality_score
            FROM companies c
            WHERE {where_sql}
            ORDER BY c.data_quality_score DESC
            LIMIT :limit OFFSET :offset
        """),
                params,
            )
            .mappings()
            .all()
        )
        _db_elapsed = (_perf_time.perf_counter() - _q_start) * 1000
        global _DB_TIME_MS, _QUERY_COUNT
        _DB_TIME_MS += _db_elapsed
        _QUERY_COUNT += 2
        items = []
        for r in rows:
            row = dict(r)
            if row.get("data_quality_score") is not None:
                row["data_quality_score"] = float(row["data_quality_score"])
            row = normalize_company(row)
            if _mask_active(mask):
                row = apply_kvkk_mask(row)
            items.append(row)
        result = {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": items,
        }
        if search and request is not None:
            session = _get_session(request)
            user_email = session.user.email if session and session.user else "anonymous"
            user_id = session.user.user_id if session and session.user else "anon"
            _log_search_event(
                user_id=user_id,
                email=user_email,
                ip=request.client.host if request.client else "",
                query=search,
                result_count=total,
                filters=f"limit={limit},offset={offset},min_score={min_score},max_score={max_score},nace={nace},mask={mask}",
            )
            aktivite_yaz(
                user_id=user_id,
                olay_tipi="arama",
                detay={"terim": search, "sonuc_adedi": total, "filtreler": f"limit={limit},offset={offset},min_score={min_score},max_score={max_score},nace={nace},mask={mask}"},
                basarili=total > 0,
                request=request,
            )
        cache_set(_ck, result)
        return result


@app.get("/api/companies/export")
def api_companies_export(
    format: str = "csv",
    search: str = "",
    min_score: int = 0,
    max_score: int = 100,
    source: str = "",
    sources: str = "",
    nace: str = "",
    mask: int = 0,
    _auth: str = Depends(require_api_key),
) -> Response:
    """CSV export - coklu kaynak + nace + turkce arama destekli.
    KVKK: mask=1 ile telefon/e-posta maskeli export."""
    import csv
    import io

    search = search.strip()[:MAX_SEARCH_LENGTH]
    min_score = max(0, min(min_score, 100))
    max_score = max(0, min(max_score, 100))
    nace = nace.strip()[:8]

    # Coklu kaynak: sources= oncelikli, source= geriye donuk uyum
    source_list = []
    if sources:
        source_list = [s.strip() for s in sources.split(",") if s.strip()]
    elif source:
        # source= parametresinde virgul de olabilir
        source_list = [s.strip() for s in source.split(",") if s.strip()]

    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        where_clauses = ["c.is_ankara=TRUE AND c.is_osb_member=TRUE"]
        params: dict[str, Any] = {"min_score": min_score, "max_score": max_score}

        if search:
            # PostgreSQL ILIKE + expression index kullanimi
            where_clauses.append("""
                (c.legal_name ILIKE :search
                OR c.trade_name ILIKE :search
                OR c.primary_phone ILIKE :search
                OR c.primary_email ILIKE :search
                OR c.tax_number ILIKE :search
                OR c.vergi_no ILIKE :search)
            """)
            params["search"] = f"%{search}%"

        if source_list:
            if len(source_list) == 1:
                where_clauses.append("""c.source_record_id IN (
                    SELECT sr.source_record_id
                    FROM source_records sr
                    JOIN sources s ON sr.source_id = s.source_id
                    WHERE s.source_name = :source_name
                )""")
                params["source_name"] = source_list[0]
            else:
                placeholders = []
                for i, src in enumerate(source_list):
                    key = f"src_{i}"
                    placeholders.append(f":{key}")
                    params[key] = src
                where_clauses.append(f"""c.source_record_id IN (
                    SELECT sr.source_record_id
                    FROM source_records sr
                    JOIN sources s ON sr.source_id = s.source_id
                    WHERE s.source_name IN ({", ".join(placeholders)})
                )""")

        if nace:
            where_clauses.append("c.nace_code LIKE :nace")
            params["nace"] = f"{nace}%"

        where_clauses.append("c.data_quality_score >= :min_score")
        where_clauses.append("c.data_quality_score <= :max_score")

        where_sql = " AND ".join(where_clauses)

        _q_start = _perf_time.perf_counter()
        rows = (
            conn.execute(
                text(f"""
            SELECT c.legal_name, c.trade_name, c.website_domain, c.primary_phone, c.primary_email,
                   c.tax_number, c.vergi_no, c.osb_parsel, c.nace_code, c.data_quality_score
            FROM companies c
            WHERE {where_sql}
            ORDER BY c.created_at DESC
            LIMIT :limit
        """),
                {**params, "limit": MAX_COMPANIES_LIMIT},
            )
            .mappings()
            .all()
        )
        _db_elapsed = (_perf_time.perf_counter() - _q_start) * 1000
        global _DB_TIME_MS, _QUERY_COUNT
        _DB_TIME_MS += _db_elapsed
        _QUERY_COUNT += 1

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Firma Adi",
                "Ticaret Adi",
                "Web",
                "Telefon",
                "E-posta",
                "VKN",
                "NACE",
                "Skor",
            ]
        )
        for r in rows:
            row = normalize_company(dict(r))
            if _mask_active(mask):
                row = apply_kvkk_mask(row)
            writer.writerow(
                [
                    row.get("legal_name", ""),
                    row.get("trade_name", ""),
                    row.get("website_domain", ""),
                    row.get("primary_phone", ""),
                    row.get("primary_email", ""),
                    row.get("tax_number") or row.get("vergi_no", ""),
                    row.get("nace_code", ""),
                    row.get("data_quality_score", ""),
                ]
            )

        csv_data = output.getvalue()
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=companies.csv"},
        )


# â”€â”€ Y19: V9 Smart Matching MVP â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# NACE ana-grup komşuluk ağırlıkları (tamamlayıcı sektörler; 1.0 = aynı grup).
# Kaynak: OSTIM/Ankara üretim zinciri kurgusu (montaj<-yan sanayi<-hammadde).
_NACE_KOMSU = {
    "29": {"28": 0.75, "25": 0.65, "24": 0.45, "46": 0.55},
    "28": {"29": 0.75, "25": 0.70, "24": 0.50, "46": 0.55},
    "25": {"28": 0.70, "29": 0.65, "24": 0.45, "23": 0.40},
    "10": {"46": 0.60, "01": 0.50, "11": 0.40},
    "62": {"63": 0.75, "58": 0.55},
    "41": {"43": 0.80, "23": 0.50, "25": 0.40},
    "24": {"25": 0.60, "28": 0.50, "29": 0.45},
    "46": {"10": 0.55, "29": 0.50, "28": 0.50},
    "43": {"41": 0.80, "23": 0.50},
}


def _nace_grup(nace: str) -> str:
    return (nace or "").split(".")[0].strip()


def _match_puan(
    row,
    buyer_grup: str,
    buyer_osb: str,
    mode: str,
    yon: str = "tedarikci",
    buyer_profil: dict | None = None,
):
    """Firma için 0-100 eşleştirme puanı + bileşen kırılımı. (None = elensin)

    yon (Y22 - eslestirme yonu):
    - tedarikci: buyer tedarikçi arıyor (montaj -> yan sanayi/hammadde; varsayilan)
    - musteri:   buyer musteri/satis kanali arıyor (yon TERS: hedef firmanin
                 komsuluk haritasindan buyer grubuna agirlik - orn. yedek parcaciga
                 45.20 servis / 46.75 toptan firmalari)
    - rakip:     sadece ayni NACE ana grubu (rakip analizi)
    """
    hedef_grup = _nace_grup(row.get("nace_code") or "")
    if not hedef_grup:
        return None

    # 1) sektör uyumu (0-45)
    if hedef_grup == buyer_grup:
        sektor = 45.0
        iliski = "ayni-sektor"
    elif yon == "rakip":
        sektor = 0.0
        iliski = "farkli"
    elif yon == "musteri" and mode == "komple":
        # ters yon: hedef firmanin ayni-sektor inanlari kimlere satar?
        kom = _NACE_KOMSU.get(hedef_grup, {}).get(buyer_grup, 0.0)
        sektor = 45.0 * kom
        iliski = "musteri-kanal" if kom >= 0.4 else "musteri-uzak"
    elif mode == "komple" and buyer_grup in _NACE_KOMSU:
        kom = _NACE_KOMSU[buyer_grup].get(hedef_grup, 0.0)
        sektor = 45.0 * kom
        iliski = "komple-sektor" if kom >= 0.4 else "uzak-sektor"
    else:
        sektor = 0.0
        iliski = "farkli"

    # 2) konum (0-20)
    hedef_osb = row.get("osb_id") or ""
    if buyer_osb and hedef_osb and hedef_osb == buyer_osb:
        konum = 20.0
    elif row.get("is_ankara"):
        konum = 12.0
    else:
        konum = 0.0

    # 3) firma kalitesi (0-25)
    try:
        kalite = min(max(float(row.get("data_quality_score") or 0), 0), 100) * 0.25
    except (TypeError, ValueError):
        kalite = 0.0

    # 4) kanıt gücü (0-10): web 5 + email 3 + telefon 2
    kanit = (
        (5.0 if row.get("web_sitesi") else 0.0)
        + (3.0 if row.get("primary_email") else 0.0)
        + (2.0 if row.get("primary_phone") else 0.0)
    )

    # 5) X03: buyer profili bonusu (0-5): olcek uyumu + sertifika + amac
    bonus, bonus_nedenler = _profil_bonus(buyer_profil, row)

    return {
        "puan": round(min(sektor + konum + kalite + kanit + bonus, 100.0), 1),
        "kirilim": {
            "sektor": round(sektor, 1),
            "konum": round(konum, 1),
            "kalite": round(kalite, 1),
            "kanit": round(kanit, 1),
            "profil": round(bonus, 1),
        },
        "iliski": iliski,
        "profil_bonus": bonus_nedenler,
    }


# Y26/X03: calisan sayisi araliklarinin buyukluk sirasi (olcek uyumu icin)
_EMPLOYEE_SCALE = {"1-5": 1, "6-20": 2, "21-50": 3, "51-250": 4, "250+": 5}


def _profil_bonus(buyer_profil: dict | None, hedef_row: dict) -> tuple[float, list]:
    """X03 MATCH v3: buyer profilinden bonus puan (0-5, toplam 100'e yuvarlanir).

    - olcek uyumu (0-2): hedef firmanin kalite skoru + kanit gucu, buyer'in
      calisan sayisina gore "kapasite sinyali" verir; buyuk buyer daha olgun
      (kayitli/verili) tedarikci ister.
    - sertifika bonusu (0-2): buyer sertifikali ve hedef firma kalitesi yuksekse
      kucuk bonus (hedef firmanin sertifikasyon verisi su an yok; vekil sinyal).
    - amac uyumu (0-1): buyer'in goal'i ile arama yonu ayni yonde ise +1.
    """
    if not buyer_profil:
        return 0.0, []
    bonus = 0.0
    nedenler = []
    # 1) olcek uyumu (0-2)
    buyer_scale = _EMPLOYEE_SCALE.get(buyer_profil.get("employee_range") or "")
    if buyer_scale_uygun(buyer_profil, hedef_row):
        bonus += 2.0
        nedenler.append("olcek-uyum")
    # 2) sertifika sinyali (0-2): buyer sertifikalarini yazmis ise
    #    kanit gucu yuksek (web+email) firmalari tercih et
    if (buyer_profil.get("certificates") or "").strip():
        cert_sinyal = (2.0 if hedef_row.get("web_sitesi") else 0.0) + (
            1.0 if hedef_row.get("primary_email") else 0.0
        )
        bonus += min(cert_sinyal, 2.0)
        if cert_sinyal > 0:
            nedenler.append("sertifika-kapasite")
    # 3) amac uyumu (0-1)
    goal = (buyer_profil.get("goal") or "").strip()
    if goal and goal != "tumu":
        bonus += 1.0
        nedenler.append("amac-uyum")
    return bonus, nedenler


def buyer_scale_uygun(buyer_profil: dict, hedef_row: dict) -> bool:
    """Buyer'in calisan sayisina gore hedef firmanin kapasite sinyali yeterli mi?
    companies tablosunda calisan sayisi yok; vekil: kalite skoru + kanit gucu.
    Buyer buyudukce daha yuksek kalite/kanit esigi bekler."""
    buyer_scale = _EMPLOYEE_SCALE.get(buyer_profil.get("employee_range") or "", 0)
    if buyer_scale <= 0:
        return False
    try:
        kalite = float(hedef_row.get("data_quality_score") or 0)
    except (TypeError, ValueError):
        kalite = 0.0
    kanit = (
        (1 if hedef_row.get("web_sitesi") else 0)
        + (1 if hedef_row.get("primary_email") else 0)
        + (1 if hedef_row.get("primary_phone") else 0)
    )
    # olcek arttikca beklenti artar: kucuk buyer kalite>40 yeter, buyuk 70+
    esik = 30.0 + buyer_scale * 8.0
    return kalite >= esik or (kalite >= 40 and kanit >= 2)


@app.get("/api/match")
def api_match(
    buyer_id: str = "",
    nace: str = "",
    osb_id: str = "",
    mode: str = "komple",
    yon: str = "tedarikci",
    min_puan: int = 30,
    limit: int = 20,
    offset: int = 0,
    mask: int = 0,
    user_token: str = "",
    _auth: str = Depends(require_api_key),
) -> dict:
    """V9 smart matching MVP: buyer profiline uygun firmaları puanla.

    - buyer_id verirse: DB'den buyer alınır (nace + osb)
    - yoksa nace (+ opsiyonel osb_id) ile serbest profil
    - mode: komple (komşu sektörler dahil) | ayni (sadece aynı ana grup)
    - yon (Y22): tedarikci (varsayilan) | musteri (ters yon satis kanali) | rakip
      (sadece ayni grup; rakip analizi)
    - user_token: onaylı kullanıcı tokenı â†’ 1 kredi düşülür; kredi bittiyse
      sonuçlar otomatik maskelenir + credit_pack önerisi döner
    """
    mode = mode if mode in ("komple", "ayni") else "komple"
    yon = yon if yon in ("tedarikci", "musteri", "rakip") else "tedarikci"
    limit = max(1, min(limit, 100))

    user = _user_from_token(user_token) if user_token else None
    tier = user.get("tier", "terminal")  # Default to terminal
    credit_info = None
    if user is not None and user["status"] == "onayli":
        kalan = _charge_module_credit(str(user["user_id"]), tier, "match")
        if kalan >= 0 and kalan == 0:
            mask = 1  # kredi bitti: sonuc maskele (V8 Credit Exhaustion UX)
            credit_info = {
                "credit_balance": 0,
                "notice": "Krediniz tükendi â€” sonuçlar maskeli görüntüleniyor.",
                "credit_pack": "750 TRY / 50 kredi (credit pack ile devam edebilirsiniz)",
            }
        else:
            credit_info = {"credit_balance": kalan if kalan >= 0 else "sinirsiz"}

    buyer_nace, buyer_osb, buyer_adi = nace, osb_id, None
    engine = get_engine()
    buyer_profil = None
    if buyer_id:
        try:
            uuid.UUID(buyer_id)
        except (ValueError, AttributeError, TypeError):
            raise HTTPException(status_code=404, detail=f"buyer bulunamadi: {buyer_id}")
        with engine.connect() as conn:
            r = (
                conn.execute(
                    text(
                        "SELECT company_id, legal_name, nace_code, osb_id FROM companies "
                        "WHERE company_id = :id"
                    ),
                    {"id": buyer_id},
                )
                .mappings()
                .first()
            )
        if not r:
            raise HTTPException(status_code=404, detail=f"buyer bulunamadi: {buyer_id}")
        buyer_nace = r["nace_code"] or buyer_nace
        buyer_osb = r["osb_id"] or buyer_osb
        buyer_adi = r["legal_name"]

    # X03 MATCH v3: girisli kullanicinin profili skorlamaya katilir
    if user is not None:
        with engine.connect() as conn:
            up = (
                conn.execute(
                    text(
                        "SELECT employee_range, certificates, goal, target_nace FROM users "
                        "WHERE user_id = :u"
                    ),
                    {"u": str(user["user_id"])},
                )
                .mappings()
                .first()
            )
        if up:
            buyer_profil = dict(up)

    buyer_grup = _nace_grup(buyer_nace)
    if not buyer_grup:
        raise HTTPException(
            status_code=400,
            detail="buyer nace belirtilmeli (buyer_id veya nace parametresi)",
        )

    with engine.connect() as conn:
        rows = (
            conn.execute(
                text(
                    "SELECT company_id, legal_name, trade_name, nace_code, nace_name, osb_id, "
                    "is_ankara, is_osb_member, data_quality_score, web_sitesi, primary_phone, "
                    "primary_email, website_domain "
                    "FROM companies WHERE nace_code IS NOT NULL AND is_ankara = TRUE "
                    "ORDER BY data_quality_score DESC NULLS LAST LIMIT 5000"
                )
            )
            .mappings()
            .all()
        )

    skorlu = []
    for r in rows:
        d = dict(r)
        if buyer_id and d.get("company_id") == buyer_id:
            continue  # kendisi
        m = _match_puan(d, buyer_grup, buyer_osb or "", mode, yon, buyer_profil)
        if not m or m["puan"] < min_puan:
            continue
        d["match"] = m
        d = normalize_company(d)
        if _mask_active(mask):
            d = apply_kvkk_mask(d)
        skorlu.append(d)

    skorlu.sort(key=lambda x: x["match"]["puan"], reverse=True)
    return {
        "buyer": {
            "buyer_id": buyer_id or None,
            "adi": buyer_adi,
            "nace": buyer_nace,
            "nace_grup": buyer_grup,
            "osb_id": buyer_osb or None,
        },
        "mode": mode,
        "yon": yon,
        "profil_uygulandi": bool(buyer_profil),
        "toplam": len(skorlu),
        "limit": limit,
        "offset": offset,
        "items": skorlu[offset : offset + limit],
        "credit": credit_info,
    }


# â”€â”€ Monetizasyon MVP (V7 Hybrid Credit) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

import hashlib
import hmac
import time as _time

_FREE_DOMAINS = {
    "gmail.com",
    "hotmail.com",
    "outlook.com",
    "yandex.com",
    "yahoo.com",
    "hotmail.com.tr",
    "yandex.com.tr",
    "icloud.com",
    "protonmail.com",
}
_TIER_CREDITS = {"terminal": 100, "strategic": 500, "enterprise": 0}  # 0 = sinirsiz
_DASH_SECRET = os.getenv(
    "DASH_SECRET", (os.getenv("DASH_API_KEY") or "huginn-secret") + "-secret"
)


def _user_token(email: str) -> str:
    """MVP auth: e-posta + zaman damgali HMAC token (24 saat gecerli)."""
    exp = int(_time.time()) + 86400
    sig = hmac.new(
        _DASH_SECRET.encode(), f"{email}:{exp}".encode(), hashlib.sha256
    ).hexdigest()[:32]
    return f"{email}|{exp}|{sig}"


_PBKDF2_ITER = 120_000


def _hash_password(password: str) -> str:
    """PBKDF2-SHA256, rastgele 16 bayt salt; format: pbkdf2$iter$salt$hash."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ITER)
    return f"pbkdf2${_PBKDF2_ITER}${salt.hex()}${dk.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        _, iters, salt_hex, hash_hex = stored.split("$")
        dk = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iters)
        )
        return hmac.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False


def _user_from_token(token: str):
    """Token'dan kullaniciyi dogrular; gecersizse None."""
    try:
        email, exp, sig = token.split("|")
        if int(exp) < int(_time.time()):
            return None
        ok = hmac.new(
            _DASH_SECRET.encode(), f"{email}:{exp}".encode(), hashlib.sha256
        ).hexdigest()[:32]
        if not hmac.compare_digest(ok, sig):
            return None
        engine = get_engine()
        with engine.connect() as conn:
            row = (
                conn.execute(
                    text(
                        "SELECT user_id, email, company_name, role, status, tier, credit_balance, api_key "
                        "FROM users WHERE email = :e"
                    ),
                    {"e": email},
                )
                .mappings()
                .first()
            )
        return row
    except Exception:
        return None


def _charge_credit(user_id: str, email: str, reason: str, amount: int = 1) -> int:
    """Kredi dusurur (enterprise sinirsiz); yeni bakiyeyi dondurur."""
    engine = get_engine()
    with engine.begin() as conn:
        row = (
            conn.execute(
                text("SELECT tier, credit_balance FROM users WHERE user_id = :u"),
                {"u": user_id},
            )
            .mappings()
            .first()
        )
        if not row:
            return 0
        if row["tier"] == "enterprise":
            return -1  # sinirsiz
        yeni = max(int(row["credit_balance"] or 0) - amount, 0)
        conn.execute(
            text(
                "UPDATE users SET credit_balance = :b, updated_at = CURRENT_TIMESTAMP "
                "WHERE user_id = :u"
            ),
            {"b": yeni, "u": user_id},
        )
        conn.execute(
            text(
                "INSERT INTO credit_ledger (user_id, delta, reason, balance_after) "
                "VALUES (:u, :d, :r, :b)"
            ),
            {"u": user_id, "d": -amount, "r": reason, "b": yeni},
        )
    return yeni


def _charge_module_credit(user_id: str, tier: str, module: str) -> int:
    """D-206: Modül kontörü düş. `module_cost` tablosundan maliyeti oku, `_charge_credit()` çağır.
    
    Args:
        user_id: Kullanıcı ID
        tier: Tier (terminal/strategic/enterprise)
        module: Modül (match/ilan/analiz/teklif/kapasite)
    
    Returns:
        Yeni bakiye | -1 (enterprise serbest) | 0 (DB error)
    """
    engine = get_engine()
    with engine.connect() as conn:
        # module_cost tablosundan maliyet oku
        cost_row = (
            conn.execute(
                text(
                    "SELECT cost_per_query FROM module_cost "
                    "WHERE module_id = :mod AND tier = :t AND effective_to IS NULL"
                ),
                {"mod": module, "t": tier},
            )
            .mappings()
            .first()
        )
        if not cost_row:
            return 0  # Modül/tier kombinasyonu bulunamadı
        
        cost = int(cost_row["cost_per_query"] or 0)
        if cost == 0:
            return -1  # Serbest (enterprise veya kapalı modül)
    
    # Krediye düşür
    reason = f"module:{module}:{tier}"
    return _charge_credit(user_id, "", reason, cost)


@app.post("/api/buyer/register")
def api_buyer_register(req: dict):
    """Kurumsal e-posta + sifre ile kayit. Kurumsal domain dogrulamasi + KVKK zorunlu.
    Sifre PBKDF2-SHA256 ile hash'lenir (ham sifre DB'ye yazilmaz).
    Sonuc: status=onay_bekliyor (admin onayindan sonra onayli + kredi yuklenir)."""
    email = (req.get("email") or "").strip().lower()
    company_name = (req.get("company_name") or "").strip()
    kvkk = bool(req.get("kvkk_consent"))
    password = req.get("password") or ""
    if not email or "@" not in email or not company_name:
        raise HTTPException(status_code=400, detail="email ve company_name zorunlu")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="sifre en az 8 karakter olmali")
    domain = email.split("@")[-1]
    if domain.lower() in _FREE_DOMAINS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"'{domain}' kurumsal degil. Lutfen sirket e-postanizla kayit olun "
                "(gmail/outlook vb. kabul edilmez)."
            ),
        )
    if not kvkk:
        raise HTTPException(
            status_code=400, detail="KVKK aydinlatma metni onayı zorunlu"
        )

    # mevcut 14k kayitla eslesme (web domain eslestirmesi)
    linked = None
    engine = get_engine()
    with engine.begin() as conn:
        dup = conn.execute(
            text("SELECT user_id, status FROM users WHERE email = :e"), {"e": email}
        ).first()
        if dup:
            raise HTTPException(status_code=409, detail="Bu e-posta zaten kayitli")
        # firma eslestirme: web domain veya benzer unvan
        cweb = (
            (req.get("website") or "")
            .replace("https://", "")
            .replace("http://", "")
            .replace("www.", "")
            .strip("/")
        )
        if cweb:
            l = conn.execute(
                text(
                    "SELECT company_id FROM companies WHERE website_domain = :w LIMIT 1"
                ),
                {"w": cweb},
            ).scalar()
            linked = l
        conn.execute(
            text("""
            INSERT INTO users (email, email_domain, company_name, linked_company_id, nace_code,
                               products_desc, target_nace, goal, contact_name, website,
                               kvkk_consent, password_hash, status)
            VALUES (:email, :domain, :company_name, :linked, :nace, :products, :target,
                    :goal, :contact, :website, :kvkk, :phash, 'onay_bekliyor')
        """),
            {
                "email": email,
                "domain": domain,
                "company_name": company_name,
                "linked": linked,
                "nace": req.get("nace_code"),
                "products": req.get("products_desc"),
                "target": req.get("target_nace"),
                "goal": req.get("goal", "tumu"),
                "contact": req.get("contact_name"),
                "website": req.get("website"),
                "kvkk": kvkk,
                "phash": _hash_password(password),
            },
        )
    return {
        "ok": True,
        "status": "onay_bekliyor",
        "message": (
            "Kaydınız alındı. Kurumsal e-posta doğrulaması ve üyelik onayından sonra "
            "krediniz yüklenecek. Onay genellikle 1 iş günü içinde tamamlanır."
        ),
        "linked_company_id": str(linked) if linked else None,
    }


@app.get("/api/buyer/categories")
def api_buyer_categories(_auth: str = Depends(require_api_key)) -> dict:
    """Urun katalogu (kayit formunda hedef sektor/urun secimi icin)."""
    engine = get_engine()
    with engine.connect() as conn:
        rows = (
            conn.execute(
                text(
                    "SELECT code, label_tr, nace_group, description FROM product_categories "
                    "WHERE active = TRUE ORDER BY nace_group, label_tr"
                )
            )
            .mappings()
            .all()
        )
    return {"items": [dict(r) for r in rows]}


@app.get("/api/buyer/profile")
def api_buyer_profile(token: str = ""):
    """Isletmem sayfasi: profil + kredi + son hareketler."""
    u = _user_from_token(token)
    if not u:
        raise HTTPException(status_code=401, detail="oturum gecersiz veya suresi doldu")
    engine = get_engine()
    with engine.connect() as conn:
        prof = (
            conn.execute(
                text(
                    "SELECT u.user_id, u.email, u.company_name, u.nace_code, u.products_desc, "
                    "u.target_nace, u.goal, u.contact_name, u.website, u.department, u.kvkk_consent, "
                    "u.employee_range, u.certificates, u.tax_number, u.phone, "
                    "u.trade_name, u.address, "
                    "u.status, u.tier, u.credit_balance, u.api_key, u.linked_company_id, u.created_at "
                    "FROM users u WHERE u.user_id = :u"
                ),
                {"u": u["user_id"]},
            )
            .mappings()
            .first()
        )
        ledger = (
            conn.execute(
                text(
                    "SELECT delta, reason, balance_after, created_at FROM credit_ledger "
                    "WHERE user_id = :u ORDER BY created_at DESC LIMIT 12"
                ),
                {"u": u["user_id"]},
            )
            .mappings()
            .all()
        )
        kategori = (
            conn.execute(
                text(
                    "SELECT code, label_tr, nace_group FROM product_categories "
                    "WHERE active = TRUE ORDER BY nace_group, label_tr"
                )
            )
            .mappings()
            .all()
        )
    p = dict(prof) if prof else {}
    # profil tamamlanma skoru (ne kadar cok bilgi = o kadar iyi eslesme)
    alanlar = [
        "company_name",
        "nace_code",
        "products_desc",
        "target_nace",
        "goal",
        "department",
        "website",
        "contact_name",
        "employee_range",
        "certificates",
    ]
    dolu = sum(1 for a in alanlar if p.get(a))
    p["profil_tamlama"] = round(dolu / len(alanlar) * 100)
    return {
        "profil": p,
        "ledger": [dict(r) for r in ledger],
        "kategoriler": [dict(r) for r in kategori],
    }


@app.put("/api/buyer/profile")
def api_buyer_profile_update(req: dict, token: str = ""):
    """Isletmem sayfasindan profil guncelleme (gonullu + onayli kullanici)."""
    u = _user_from_token(token)
    if not u:
        raise HTTPException(status_code=401, detail="oturum gecersiz veya suresi doldu")
    alanlar = {
        "company_name": req.get("company_name"),
        "nace_code": req.get("nace_code"),
        "products_desc": req.get("products_desc"),
        "target_nace": req.get("target_nace"),
        "goal": req.get("goal"),
        "contact_name": req.get("contact_name"),
        "website": req.get("website"),
        "department": req.get("department"),
        "employee_range": req.get("employee_range"),
        "certificates": req.get("certificates"),
        "tax_number": req.get("tax_number"),
        "phone": req.get("phone"),
        "trade_name": req.get("trade_name"),
        "address": req.get("address"),
    }
    sets, params = [], {"u": str(u["user_id"])}
    for k, v in alanlar.items():
        if v is not None:
            sets.append(f"{k} = :{k}")
            params[k] = str(v).strip()
    if not sets:
        raise HTTPException(status_code=400, detail="guncellenecek alan yok")
    sets.append("updated_at = CURRENT_TIMESTAMP")
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(f"UPDATE users SET {', '.join(sets)} WHERE user_id = :u"), params
        )
        row = (
            conn.execute(
                text(
                    "SELECT company_name, nace_code, products_desc, target_nace, goal, department, "
                    "website, contact_name, employee_range, certificates, tax_number, phone, "
                    "trade_name, address, credit_balance, tier "
                    "FROM users WHERE user_id = :u"
                ),
                {"u": str(u["user_id"])},
            )
            .mappings()
            .first()
        )
    alanlar_dolu = sum(
        1
        for a in [
            "company_name",
            "nace_code",
            "products_desc",
            "target_nace",
            "goal",
            "department",
            "website",
            "contact_name",
            "employee_range",
            "certificates",
        ]
        if row.get(a)
    )
    return {
        "ok": True,
        "profil_tamlama": round(alanlar_dolu / 10 * 100),
        "profil": dict(row),
    }


@app.get("/api/buyer/ledger")
def api_buyer_ledger(token: str = "", limit: int = 20):
    u = _user_from_token(token)
    if not u:
        raise HTTPException(status_code=401, detail="oturum gecersiz veya suresi doldu")
    engine = get_engine()
    with engine.connect() as conn:
        rows = (
            conn.execute(
                text(
                    "SELECT delta, reason, balance_after, created_at FROM credit_ledger "
                    "WHERE user_id = :u ORDER BY created_at DESC LIMIT :l"
                ),
                {"u": u["user_id"], "l": max(1, min(limit, 50))},
            )
            .mappings()
            .all()
        )
    return {"items": [dict(r) for r in rows]}


@app.post("/api/buyer/login")
def api_buyer_login(req: dict, request: Request, response: Response):
    """E-posta + sifre ile giris. Sifresi olmayan eski MVP kayitlarina ozel:
    password bos gonderilirse ve DB'de hash yoksa giris izin verilir (gecis donemi).
    Onayli kullaniciya 24 saatlik token doner; kredi bakiyesi dahil.
    DASH-01 S-2: Basarili giris sonrasi HttpOnly session cookie olusturulur."""
    email = (req.get("email") or "").strip().lower()
    password = req.get("password") or ""
    if not email or "@" not in email:
        _log_login_event(
            user_id="", email=email, ip=request.client.host if request.client else "",
            user_agent=(request.headers.get("User-Agent") or "")[:500], success=False,
            error_msg="gecerli e-posta girin",
        )
        raise HTTPException(status_code=400, detail="gecerli e-posta girin")
    engine = get_engine()
    with engine.connect() as conn:
        row = (
            conn.execute(
                text(
                    "SELECT user_id, email, status, tier, credit_balance, role, company_name, password_hash "
                    "FROM users WHERE email = :e"
                ),
                {"e": email},
            )
            .mappings()
            .first()
        )
    if not row:
        _log_login_event(
            user_id="", email=email, ip=request.client.host if request.client else "",
            user_agent=(request.headers.get("User-Agent") or "")[:500], success=False,
            error_msg="kayit bulunamadi",
        )
        raise HTTPException(status_code=404, detail="Bu e-posta ile kayit bulunamadi")
    stored = row["password_hash"]
    if stored and not _verify_password(password, stored):
        _log_login_event(
            user_id=row.get("user_id", ""), email=row["email"],
            ip=request.client.host if request.client else "",
            user_agent=(request.headers.get("User-Agent") or "")[:500], success=False,
            error_msg="sifre hatali",
        )
        raise HTTPException(status_code=401, detail="E-posta veya şifre hatalı")
    if not stored and len(password) < 8:
        _log_login_event(
            user_id=row.get("user_id", ""), email=row["email"],
            ip=request.client.host if request.client else "",
            user_agent=(request.headers.get("User-Agent") or "")[:500], success=False,
            error_msg="sifre hatali",
        )
        raise HTTPException(status_code=401, detail="E-posta veya şifre hatalı")
    if row["status"] != "onayli":
        durum = (
            "onayınız değerlendiriliyor"
            if row["status"] == "onay_bekliyor"
            else "kabul edilmedi"
        )
        _log_login_event(
            user_id=row.get("user_id", ""), email=row["email"],
            ip=request.client.host if request.client else "",
            user_agent=(request.headers.get("User-Agent") or "")[:500], success=False,
            error_msg="uyelik_onay",
        )
        raise HTTPException(
            status_code=403,
            detail=f"Üyelik onayı: {durum}. Sorularınız için iletişime geçin.",
        )
    # DASH-01 S-2: HttpOnly session cookie olustur (XSS'e karsi guvenli)
    from company_master.auth.session import SessionUser, create_session

    session_user = SessionUser(
        user_id=row["user_id"],
        email=row["email"],
        role=row["role"] or "user",
        tier=row["tier"] or "terminal",
        company_name=row["company_name"],
        credit_balance=row["credit_balance"] or 0,
    )
    client_ip = request.client.host if request.client else ""
    create_session(session_user, client_ip, response)
    _log_login_event(
        user_id=row["user_id"],
        email=row["email"],
        ip=client_ip,
        user_agent=(request.headers.get("User-Agent") or "")[:500],
        success=True,
    )
    return {
        "token": _user_token(row["email"]),
        "user": {
            "email": row["email"],
            "company_name": row["company_name"],
            "tier": row["tier"],
            "credit_balance": row["credit_balance"],
            "role": row["role"],
        },
    }


# DATA-LOG-01: login_events + search_events kayit yardimcilari


def _dl_mask_ip(ip: str) -> str:
    """IP son oktesini maskeler: 192.168.1.134 -> 192.168.1.0."""
    parts = ip.split(".")
    if len(parts) == 4:
        parts[-1] = "0"
        return ".".join(parts)
    return ip


# E-posta maskeleme: mevcut _mask_email (KVKK) fonksiyonunu kullanilir


def _log_login_event(
    user_id: str,
    email: str,
    ip: str,
    user_agent: str,
    success: bool,
    error_msg: str = "",
) -> None:
    """DATA-LOG-01: login_events tablosuna kayit. Hata istegi duser."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO login_events (user_id, email_masked, ts, ip_masked, "
                    "user_agent, success, method, path, error_msg) "
                    "VALUES (:uid, :email, CURRENT_TIMESTAMP, :ip, :ua, :ok, 'POST', '/api/buyer/login', :err)"
                ),
                {
                    "uid": user_id or "",
                    "email": _mask_email(email),
                    "ip": _dl_mask_ip(ip),
                    "ua": (user_agent or "")[:500],
                    "ok": 1 if success else 0,
                    "err": (error_msg or "")[:500],
                },
            )
            conn.commit()
    except Exception as exc:
        print(f"[DATA-LOG-01] login_event kayit hatasi: {exc}")


def _log_search_event(
    user_id: str,
    email: str,
    ip: str,
    query: str,
    result_count: int,
    filters: str = "",
) -> None:
    """DATA-LOG-01: search_events tablosuna kayit. Hata istegi duser."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO search_events (user_id, email_masked, ts, ip_masked, "
                    "query, result_count, filters) "
                    "VALUES (:uid, :email, CURRENT_TIMESTAMP, :ip, :q, :rc, :f)"
                ),
                {
                    "uid": user_id or "",
                    "email": _mask_email(email),
                    "ip": _dl_mask_ip(ip),
                    "q": (query or "")[:1000],
                    "rc": result_count,
                    "f": (filters or "")[:500],
                },
            )
            conn.commit()
    except Exception as exc:
        print(f"[DATA-LOG-01] search_event kayit hatasi: {exc}")




def aktivite_yaz(
    user_id: str,
    olay_tipi: str,
    detay: dict | None = None,
    basarili: bool = True,
    request: Request | None = None,
) -> None:
    """API-ADMIN-AKTIVITE-YAZ-14: user_activity_log tablosuna kayit.

    Hata istek dusurmez (best-effort). Olay tipleri: 'giris', 'arama', 'ai_kullanim'.
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            ip = ""
            if request and request.client:
                ip = request.client.host
            
            import json
            conn.execute(
                text(
                    "INSERT INTO user_activity_log (user_id, olay_tipi, olay_zamani, detay, "
                    "basarili, ip_adresi, ulke_kodu) "
                    "VALUES (:uid, :tip, CURRENT_TIMESTAMP, :detay, :ok, :ip, :ulke)"
                ),
                {
                    "uid": user_id or "",
                    "tip": olay_tipi,
                    "detay": json.dumps(detay) if detay else None,
                    "ok": basarili,
                    "ip": ip or None,
                    "ulke": None,
                },
            )
            conn.commit()
    except Exception as exc:
        print(f"[API-ADMIN-AKTIVITE-YAZ-14] aktivite kayit hatasi: {exc}")


# â”€â”€ X04: Üyelik yardımcıları (şifre sıfırlama, e-posta doğrulama, Telegram) â”€â”€â”€
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

_SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
_SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
_SMTP_USER = os.getenv("SMTP_USER", "")
_SMTP_PASS = os.getenv("SMTP_PASS", "")
_SMTP_FROM = os.getenv("SMTP_FROM", "noreply@huginn.local")

_TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
_TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
_WELCOME_TELEGRAM_CHAT_ID = os.getenv("WELCOME_TELEGRAM_CHAT_ID", _TELEGRAM_CHAT_ID)

_RESET_TOKEN_TTL = 3600  # 1 saat
_VERIFY_TOKEN_TTL = 86400  # 24 saat


def _generate_token(prefix: str = "", length: int = 32) -> str:
    """URL-safe token üretir."""
    return (
        f"{prefix}{secrets.token_urlsafe(length)}"
        if prefix
        else secrets.token_urlsafe(length)
    )


def _send_email(to: str, subject: str, html_body: str) -> bool:
    """SMTP ile e-posta gönderir. Yapılandırma yoksa sessizce False döner."""
    if not _SMTP_USER or not _SMTP_PASS:
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = _SMTP_FROM
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=10) as s:
            s.starttls()
            s.login(_SMTP_USER, _SMTP_PASS)
            s.send_message(msg)
        return True
    except Exception:
        return False


def _send_telegram(text: str, chat_id: str = "") -> bool:
    """Telegram Bot API ile mesaj gönderir. Token/chat_id yoksa False."""
    target = chat_id or _TELEGRAM_CHAT_ID
    if not _TELEGRAM_BOT_TOKEN or not target:
        return False
    try:
        import requests

        requests.post(
            f"https://api.telegram.org/bot{_TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": target, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        return True
    except Exception:
        return False


@app.post("/api/buyer/logout")
def api_buyer_logout(req: dict):
    """Cikis: istemci tarafinda token silinir; sunucu tarafi stateless oldugundan
    tokenin kalan suresi kadar gecerliligi teknik olarak surer (MVP notu: tam
    iptal icin token blocklist Scale asamasinda). Donus: ok (istemci temizler)."""
    return {"ok": True, "message": "Cikis yapildi"}


@app.post("/api/buyer/change-password")
def api_buyer_change_password(req: dict, token: str = ""):
    """Oturumdaki kullanici sifresini degistirir (PBKDF2)."""
    u = _user_from_token(token)
    if not u:
        raise HTTPException(status_code=401, detail="oturum gecersiz veya suresi doldu")
    new = req.get("new_password") or ""
    old = req.get("old_password") or ""
    if len(new) < 8:
        raise HTTPException(
            status_code=400, detail="yeni sifre en az 8 karakter olmali"
        )
    engine = get_engine()
    with engine.connect() as conn:
        row = (
            conn.execute(
                text("SELECT password_hash FROM users WHERE user_id = :u"),
                {"u": str(u["user_id"])},
            )
            .mappings()
            .first()
        )
    if row and row["password_hash"] and not _verify_password(old, row["password_hash"]):
        raise HTTPException(status_code=401, detail="mevcut sifre hatali")
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE users SET password_hash = :p, updated_at = CURRENT_TIMESTAMP "
                "WHERE user_id = :u"
            ),
            {"p": _hash_password(new), "u": str(u["user_id"])},
        )
    return {"ok": True, "message": "sifre guncellendi"}


def _store_reset_token(email: str, token: str):
    """Sıfırlama token'ını DB'ye yazar (users tablosunda reset_token, reset_token_exp)."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE users SET reset_token = :t, reset_token_exp = :e WHERE email = :em"
            ),
            {"t": token, "e": int(_time.time()) + _RESET_TOKEN_TTL, "em": email},
        )


def _store_verify_token(email: str, token: str):
    """E-posta doğrulama token'ını DB'ye yazar (users tablosunda verify_token, verify_token_exp)."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE users SET verify_token = :t, verify_token_exp = :e WHERE email = :em"
            ),
            {"t": token, "e": int(_time.time()) + _VERIFY_TOKEN_TTL, "em": email},
        )


@app.post("/api/buyer/reset-password-request")
def api_buyer_reset_password_request(req: dict):
    """Şifre sıfırlama isteği â€” e-posta alır, token üretir, e-posta/Telegram ile gönderir."""
    email = (req.get("email") or "").strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="geçerli e-posta girin")
    engine = get_engine()
    with engine.connect() as conn:
        row = (
            conn.execute(
                text("SELECT user_id, email, company_name FROM users WHERE email = :e"),
                {"e": email},
            )
            .mappings()
            .first()
        )
    if not row:
        return {
            "ok": True,
            "message": "E-posta sistemde varsa sıfırlama linki gönderilecektir.",
        }
    token = _generate_token("RST-", 24)
    _store_reset_token(email, token)
    reset_url = (
        f"{os.getenv('APP_BASE_URL', 'http://localhost:8000')}/#reset-password/{token}"
    )
    html = f"""
    <h2>Huginn Data Insights â€” Şifre Sıfırlama</h2>
    <p>Merhaba <b>{row['company_name'] or email}</b>,</p>
    <p>Şifre sıfırlama talebiniz alındı. Aşağıdaki linke tıklayarak yeni şifrenizi belirleyin:</p>
    <p><a href="{reset_url}" style="background:#3b82f6;color:#fff;padding:12px 24px;
       text-decoration:none;border-radius:6px;display:inline-block">Yeni Şifre Belirle</a></p>
    <p>Link 1 saat geçerlidir. Talebiniz değilselse bu e-postayı görmezden gelin.</p>
    <hr><small>Huginn Data Insights</small>
    """
    _send_email(email, "Huginn â€” Şifre Sıfırlama", html)
    _send_telegram(
        f"ğŸ” <b>Şifre Sıfırlama Talebi</b>\nE-posta: <code>{email}</code>\nFirma: {row['company_name'] or '-'}"
    )
    return {
        "ok": True,
        "message": "E-posta sistemde varsa sıfırlama linki gönderilecektir.",
    }


@app.post("/api/buyer/reset-password-confirm")
def api_buyer_reset_password_confirm(req: dict):
    """Şifre sıfırlama onayı â€” token + yeni şifre alır, doğrular, günceller."""
    token = (req.get("token") or "").strip()
    new_password = req.get("new_password") or ""
    if not token:
        raise HTTPException(status_code=400, detail="token zorunlu")
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="şifre en az 8 karakter olmalı")
    engine = get_engine()
    with engine.begin() as conn:
        row = (
            conn.execute(
                text(
                    "SELECT user_id, email, reset_token, reset_token_exp FROM users WHERE reset_token = :t"
                ),
                {"t": token},
            )
            .mappings()
            .first()
        )
    if not row or int(row["reset_token_exp"] or 0) < int(_time.time()):
        raise HTTPException(status_code=400, detail="geçersiz veya süresi dolmuş token")
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE users SET password_hash = :ph, reset_token = NULL, reset_token_exp = NULL, "
                "updated_at = CURRENT_TIMESTAMP WHERE user_id = :u"
            ),
            {"ph": _hash_password(new_password), "u": str(row["user_id"])},
        )
    _send_telegram(f"âœ… <b>Şifre Sıfırlandı</b>\nE-posta: <code>{row['email']}</code>")
    return {
        "ok": True,
        "message": "Şifreniz başarıyla güncellendi. Şimdi giriş yapabilirsiniz.",
    }


@app.post("/api/buyer/verify-email-request")
def api_buyer_verify_email_request(req: dict):
    """E-posta doğrulama isteği â€” kayıtlı kullanıcıya doğrulama linki gönderir."""
    email = (req.get("email") or "").strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="geçerli e-posta girin")
    engine = get_engine()
    with engine.connect() as conn:
        row = (
            conn.execute(
                text(
                    "SELECT user_id, email, company_name, status FROM users WHERE email = :e"
                ),
                {"e": email},
            )
            .mappings()
            .first()
        )
    if not row:
        return {
            "ok": True,
            "message": "E-posta sistemde varsa doğrulama linki gönderilecektir.",
        }
    if row["status"] == "onayli":
        return {"ok": True, "message": "E-posta zaten doğrulanmış."}
    token = _generate_token("VER-", 24)
    _store_verify_token(email, token)
    verify_url = (
        f"{os.getenv('APP_BASE_URL', 'http://localhost:8000')}/#verify-email/{token}"
    )
    html = f"""
    <h2>Huginn Data Insights â€” E-posta Doğrulama</h2>
    <p>Merhaba <b>{row['company_name'] or email}</b>,</p>
    <p>Hesabınızı aktifleştirmek için aşağıdaki linke tıklayın:</p>
    <p><a href="{verify_url}" style="background:#10b981;color:#fff;padding:12px 24px;
       text-decoration:none;border-radius:6px;display:inline-block">E-postamı Doğrula</a></p>
    <p>Link 24 saat geçerlidir.</p>
    <hr><small>Huginn Data Insights</small>
    """
    _send_email(email, "Huginn â€” E-posta Doğrulama", html)
    _send_telegram(
        f"ğŸ“§ <b>E-posta Doğrulama Talebi</b>\nE-posta: <code>{email}</code>\nFirma: {row['company_name'] or '-'}"
    )
    return {
        "ok": True,
        "message": "E-posta sistemde varsa doğrulama linki gönderilecektir.",
    }


@app.get("/api/buyer/verify-email/{token}")
def api_buyer_verify_email_confirm(token: str):
    """E-posta doğrulama onayı â€” token doğrulanır, status 'onayli' yapılır."""
    engine = get_engine()
    with engine.begin() as conn:
        row = (
            conn.execute(
                text(
                    "SELECT user_id, email, verify_token, verify_token_exp, status, tier, credit_balance "
                    "FROM users WHERE verify_token = :t"
                ),
                {"t": token},
            )
            .mappings()
            .first()
        )
    if not row or int(row["verify_token_exp"] or 0) < int(_time.time()):
        raise HTTPException(status_code=400, detail="geçersiz veya süresi dolmuş token")
    if row["status"] == "onayli":
        return {"ok": True, "message": "E-posta zaten doğrulanmış."}
    new_tier = row["tier"] or "terminal"
    start_credit = _TIER_CREDITS.get(new_tier, 100)
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE users SET status = 'onayli', tier = :tier, credit_balance = :cred, "
                "verify_token = NULL, verify_token_exp = NULL, updated_at = CURRENT_TIMESTAMP "
                "WHERE user_id = :u"
            ),
            {"tier": new_tier, "cred": start_credit, "u": str(row["user_id"])},
        )
        if start_credit > 0:
            conn.execute(
                text(
                    "INSERT INTO credit_ledger (user_id, delta, reason, balance_after) "
                    "VALUES (:u, :d, 'Kayıt başlangıç kredisi', :b)"
                ),
                {"u": str(row["user_id"]), "d": start_credit, "b": start_credit},
            )
    _send_telegram(
        f"âœ… <b>E-posta Doğrulandı</b>\nE-posta: <code>{row['email']}</code>\nTier: {new_tier} Â· Kredi: {start_credit}"
    )
    welcome_text = (
        f"ğŸ‰ <b>Hoş Geldiniz!</b>\n"
        f"Firma: {row['company_name'] or row['email']}\n"
        f"Paket: <b>{new_tier.title()}</b>\n"
        f"Başlangıç Kredisi: <b>{start_credit}</b>\n\n"
        f"ğŸ” Akıllı Eşleştirme ile tedarikçi/müşteri/rakip analizlerinizi başlatabilirsiniz.\n"
        f"ğŸ“Š Veri Sağlığı paneliyle veri kalitenizi takip edin.\n"
        f"ğŸ“š Bilgi Merkezi'nden arama ipuçlarını inceleyin."
    )
    _send_telegram(welcome_text, _WELCOME_TELEGRAM_CHAT_ID)
    return {
        "ok": True,
        "message": "E-posta doğrulandı. Hesabınız aktifleştirildi.",
        "tier": new_tier,
        "credit": start_credit,
    }


@app.post("/api/buyer/welcome-telegram")
def api_buyer_welcome_telegram(req: dict):
    """Admin/uygulama tarafından çağrılır â€” onaylı kullanıcıya hoşgeldin Telegram mesajı."""
    token = (req.get("user_token") or "").strip()
    u = _user_from_token(token)
    if not u or u["status"] != "onayli":
        raise HTTPException(status_code=403, detail="sadece onaylı kullanıcılar için")
    text = (
        f"ğŸ‰ <b>Huginn Data Insights'e Hoş Geldiniz!</b>\n"
        f"Firma: <b>{u['company_name']}</b>\n"
        f"Paket: <b>{u['tier'].title()}</b>\n"
        f"Kredi: <b>{u['credit_balance']}</b>\n\n"
        f"ğŸ” Akıllı Eşleştirme: tedarikçi/müşteri/rakip analizi\n"
        f"ğŸ“Š Veri Sağlığı: veri kalitesi & kapsama\n"
        f"ğŸ“š Bilgi Merkezi: arama ipuçları & CSV dışa aktarım\n\n"
        f"Sorularınız için: <code>admin@huginn.local</code>"
    )
    sent = _send_telegram(text, _WELCOME_TELEGRAM_CHAT_ID)
    return {
        "ok": sent,
        "message": (
            "Telegram mesajı gönderildi" if sent else "Telegram yapılandırılmamış"
        ),
    }


@app.get("/api/me")
def api_me(token: str = ""):
    u = _user_from_token(token)
    if not u:
        raise HTTPException(status_code=401, detail="oturum gecersiz veya suresi doldu")
    return {"user": dict(u)}


# â”€â”€ Admin: onay kuyrugu + kredi yonetimi (DASH_API_KEY ile) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def require_admin(
    authorization: str = Header(None, alias="Authorization"),
    x_api_key: str = Header(None, alias="X-API-Key"),
    api_key: str = "",
):
    """Yonetici erisimi: DASH_API_KEY VEYA role=admin kullanici tokeni (Bearer).

    SEC-01: Fail-closed. DASH_API_KEY tanimli degilse key tabanli yonetici
    erisimi kapalidir (bos anahtar "" == "" eslesmesi yonetici acamaz).
    """
    admin_key = (os.getenv("DASH_API_KEY") or "").strip()
    provided_key = (x_api_key or api_key or "").strip()
    if admin_key and provided_key and provided_key == admin_key:
        return "admin-key"
    if authorization:
        tok = authorization.replace("Bearer ", "").strip()
        u = _user_from_token(tok)
        if u and u.get("role") == "admin" and u.get("status") == "onayli":
            return "admin-user"
    raise HTTPException(status_code=403, detail="Yonetici erisimi gerekli")





def require_admin_role(
    authorization: str = Header(None, alias="Authorization"),
    x_api_key: str = Header(None, alias="X-API-Key"),
    api_key: str = "",
):
    """Admin rolü kontrolü: DASH_API_KEY VEYA role=admin kullanici tokeni.

    Sadece role=admin olan kullanıcılar erişebilir.
    """
    admin_key = (os.getenv("DASH_API_KEY") or "").strip()
    provided_key = (x_api_key or api_key or "").strip()
    if admin_key and provided_key and provided_key == admin_key:
        return "admin-key"
    if authorization:
        tok = authorization.replace("Bearer ", "").strip()
        u = _user_from_token(tok)
        if u and u.get("role") == "admin" and u.get("status") == "onayli":
            return "admin-user"
    raise HTTPException(status_code=403, detail="Admin rolü gerekli")


@app.post("/api/admin/login")
def api_admin_login_post(req: dict, request: Request, _rate: None = Depends(_auth_rate_guard)):
    """ADMIN-GATE-01: POST admin girişi. {email, password} → token.

    SEC-AUTH-01 Y-1: `_auth_rate_guard` IP bazlı katı limit uygular.
    Y-2: bilinmeyen e-posta ve hatalı şifre aynı 401 detayını döner
    (var/yok sızması engellenir).
    """
    email = (req.get("email") or "").strip()
    password = req.get("password") or ""
    if not email or not password:
        aktivite_yaz(user_id=email, olay_tipi="giris", basarili=False, request=request)
        raise HTTPException(status_code=400, detail="email ve sifre zorunlu")
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT email, password_hash, role, status FROM users WHERE email = :e"),
            {"e": email},
        ).mappings().first()
    if row:
        if row["status"] != "onayli" or row["role"] != "admin":
            aktivite_yaz(user_id=email, olay_tipi="giris", basarili=False, request=request)
            raise HTTPException(status_code=403, detail="admin yetkisi gerekli")
        if not _verify_password(password, row["password_hash"]):
            aktivite_yaz(user_id=email, olay_tipi="giris", basarili=False, request=request)
            raise HTTPException(status_code=401, detail="gecersiz email veya sifre")
        # API-ADMIN-LASTLOGIN-YAZ-05: Başarılı girişte last_login güncelle
        with engine.connect() as conn:
            conn.execute(
                text("UPDATE users SET last_login = NOW() WHERE email = :e"),
                {"e": email},
            )
            conn.commit()
        aktivite_yaz(user_id=row["email"], olay_tipi="giris", basarili=True, request=request)
        return {"token": _user_token(row["email"])}
    try:
        secrets_path = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"
        if secrets_path.exists():
            with secrets_path.open("rb") as f:
                secrets = tomllib.load(f)
            admin_pw = secrets.get("admin_password", "")
            if admin_pw and email == "admin@huginn.local" and admin_pw == password:
                # API-ADMIN-LASTLOGIN-YAZ-05: Fallback admin için de last_login güncelle
                with engine.connect() as conn:
                    conn.execute(
                        text("UPDATE users SET last_login = NOW() WHERE email = :e"),
                        {"e": email},
                    )
                    conn.commit()
                aktivite_yaz(user_id=email, olay_tipi="giris", basarili=True, request=request)
                return {"token": _user_token(email)}
    except Exception:
        pass
    aktivite_yaz(user_id=email, olay_tipi="giris", basarili=False, request=request)
    raise HTTPException(status_code=401, detail="gecersiz email veya sifre")


@app.post("/api/admin/reset-request")
def api_admin_reset_request(req: dict, _rate: None = Depends(_auth_rate_guard)):
    """AUTH-GATE-01: Sifre sifirlama istegi. {email} -> token gonderilir.

    SEC-AUTH-01 Y-2: bilinen/bilinmeyen e-posta ayirt edilemez; yanit her
    durumda tek tip `{ok: true}` (var/yok sızması engellenir).
    """
    email = (req.get("email") or "").strip()
    if not email:
        raise HTTPException(status_code=400, detail="email zorunlu")
    try:
        _store_reset_token(email, str(uuid.uuid4()))
    except Exception:
        pass  # Y-2: hata detayı yanıta sızmaz (token yazılamadıysa da aynı yanıt)
    return {"ok": True, "message": "sifirlama linki gonderildi"}


@app.post("/api/admin/reset-confirm")
def api_admin_reset_confirm(req: dict, _rate: None = Depends(_auth_rate_guard)):
    """AUTH-GATE-01: Sifre sifirlama onay. {email, token, new_password} -> sifre guncellenir."""
    email = (req.get("email") or "").strip()
    token = req.get("token") or ""
    new_password = req.get("new_password") or ""
    if not email or not token or not new_password:
        raise HTTPException(status_code=400, detail="email, token, yeni sifre zorunlu")
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="yeni sifre en az 8 karakter")
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT password_hash FROM users WHERE email = :e "
                "AND reset_token = :t AND reset_token_exp > :now"
            ),
            {"e": email, "t": token, "now": int(_time.time())},
        ).mappings().first()
    if not row:
        raise HTTPException(status_code=400, detail="gecersiz token veya email")
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE users SET password_hash = :p, reset_token = NULL, "
                "reset_token_exp = NULL, updated_at = CURRENT_TIMESTAMP "
                "WHERE email = :e"
            ),
            {"p": _hash_password(new_password), "e": email},
        )
    return {"ok": True, "message": "sifre guncellendi"}


@app.post("/api/admin/change-password")
def api_admin_change_password(
    req: dict, request: Request, token: str = "", _rate: None = Depends(_auth_rate_guard)
):
    """ADMIN-RESET-01: Oturumdaki admin kendi sifresini degistirir (PBKDF2).

    Token `?token=` veya `Authorization: Bearer` ile gelir; kullanici admin + onayli olmali.
    SEC-AUTH-01 Y-1: `_auth_rate_guard` IP bazlı katı limit uygular.
    """
    if not token and request is not None:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:].strip()
    u = _user_from_token(token)
    if not u or u.get("role") != "admin" or u.get("status") != "onayli":
        raise HTTPException(status_code=403, detail="admin yetkisi gerekli")
    # SEC-AUTH-01 D-4: .strip() kaldırıldı — login ile tutarlı; baştaki/sondaki
    # boşluk şifrenin parçasıysa doğrulama hatalı sızmasın.
    old_pw = req.get("old_password") or ""
    new_pw = req.get("new_password") or ""
    if not old_pw or not new_pw:
        raise HTTPException(status_code=400, detail="mevcut ve yeni sifre zorunlu")
    if len(new_pw) < 8:
        raise HTTPException(status_code=400, detail="yeni sifre en az 8 karakter olmali")
    if old_pw == new_pw:
        raise HTTPException(status_code=400, detail="yeni sifre eskisiyle ayni olamaz")
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT password_hash FROM users WHERE user_id = :u"),
            {"u": u["user_id"]},
        ).mappings().first()
    if not row or not _verify_password(old_pw, row["password_hash"] or ""):
        raise HTTPException(status_code=401, detail="mevcut sifre hatali")
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE users SET password_hash = :p, updated_at = CURRENT_TIMESTAMP "
                "WHERE user_id = :u"
            ),
            {"p": _hash_password(new_pw), "u": u["user_id"]},
        )
    return {"ok": True, "message": "sifre guncellendi", "email": u["email"]}


@admin_cache(ttl=60)
@app.get("/api/admin/pending")
def api_admin_pending(_auth: str = Depends(require_admin)):
    # Cache TTL: 60s
    engine = get_engine()
    with engine.connect() as conn:
        bekleyen = (
            conn.execute(
                text(
                    "SELECT user_id, email, company_name, nace_code, products_desc, target_nace, "
                    "goal, website, linked_company_id, created_at FROM users "
                    "WHERE status = 'onay_bekliyor' ORDER BY created_at"
                )
            )
            .mappings()
            .all()
        )
        son = (
            conn.execute(
                text(
                    "SELECT user_id, email, company_name, tier, credit_balance, status, updated_at "
                    "FROM users WHERE status = 'onayli' ORDER BY updated_at DESC LIMIT 10"
                )
            )
            .mappings()
            .all()
        )
    return {
        "bekleyen": [dict(r) for r in bekleyen],
        "onayli_son": [dict(r) for r in son],
    }


@app.post("/api/admin/approve")
def api_admin_approve(req: dict, _auth: str = Depends(require_admin)):
    """Onayla: tier sec (terminal/strategic/enterprise) -> kredi yukle + enterprise'a api_key uret."""
    user_id = req.get("user_id") or ""
    tier = req.get("tier") or "terminal"
    reject = bool(req.get("reject"))
    note = req.get("note") or ""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id zorunlu")
    try:
        uuid.UUID(user_id)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(status_code=400, detail="user_id UUID olmali")
    kredi = _TIER_CREDITS.get(tier, 100)
    api_key = None
    engine = get_engine()
    with engine.begin() as conn:
        u = (
            conn.execute(
                text("SELECT email, tier, status FROM users WHERE user_id = :u"),
                {"u": user_id},
            )
            .mappings()
            .first()
        )
        if not u:
            raise HTTPException(status_code=404, detail="kullanici bulunamadi")
        if reject:
            conn.execute(
                text(
                    "UPDATE users SET status='reddedildi', rejection_note=:n, "
                    "updated_at=CURRENT_TIMESTAMP WHERE user_id=:u"
                ),
                {"n": note, "u": user_id},
            )
            return {"ok": True, "status": "reddedildi"}
        if tier == "enterprise":
            api_key = (
                "ent_"
                + hmac.new(
                    _DASH_SECRET.encode(), user_id.encode(), hashlib.sha256
                ).hexdigest()[:32]
            )
            conn.execute(
                text(
                    "UPDATE users SET status='onayli', tier=:t, credit_balance=0, "
                    "api_key=:k, updated_at=CURRENT_TIMESTAMP WHERE user_id=:u"
                ),
                {"t": tier, "k": api_key, "u": user_id},
            )
            yeni = -1
        else:
            conn.execute(
                text(
                    "UPDATE users SET status='onayli', tier=:t, credit_balance=:b, "
                    "updated_at=CURRENT_TIMESTAMP WHERE user_id=:u"
                ),
                {"t": tier, "b": kredi, "u": user_id},
            )
            yeni = kredi
        conn.execute(
            text(
                "INSERT INTO credit_ledger (user_id, delta, reason, balance_after) "
                "VALUES (:u, :d, 'approve', :b)"
            ),
            {"u": user_id, "d": kredi, "b": yeni},
        )
    return {
        "ok": True,
        "status": "onayli",
        "tier": tier,
        "credit_balance": yeni,
        "api_key": api_key,
    }


@app.post("/api/admin/credit")
def api_admin_credit(req: dict, _auth: str = Depends(require_admin)):
    """Credit Pack / manuel kredi yukleme (750 TRY/50 kredi vb.)."""
    user_id = req.get("user_id") or ""
    amount = int(req.get("amount") or 0)
    if not user_id or amount <= 0:
        raise HTTPException(status_code=400, detail="user_id ve pozitif amount zorunlu")
    engine = get_engine()
    with engine.begin() as conn:
        row = (
            conn.execute(
                text("SELECT credit_balance, tier FROM users WHERE user_id = :u"),
                {"u": user_id},
            )
            .mappings()
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail="kullanici bulunamadi")
        yeni = int(row["credit_balance"] or 0) + amount
        conn.execute(
            text(
                "UPDATE users SET credit_balance=:b, updated_at=CURRENT_TIMESTAMP "
                "WHERE user_id=:u"
            ),
            {"b": yeni, "u": user_id},
        )
        conn.execute(
            text(
                "INSERT INTO credit_ledger (user_id, delta, reason, balance_after) "
                "VALUES (:u, :d, 'credit_pack', :b)"
            ),
            {"u": user_id, "d": amount, "b": yeni},
        )
    return {"ok": True, "credit_balance": yeni}


@admin_cache(ttl=300)
@app.get("/api/admin/api-usage")
def api_admin_api_usage(_auth: str = Depends(require_admin)):
    # Cache TTL: 300s
    """Y26: Tier bazli API kullanim raporu (enterprise key istek sayacları)."""
    return {"items": api_usage_snapshot(), "rate_limits": dict(_TIER_RATE_LIMITS)}


@app.post("/api/admin/rotate-key")
def api_admin_rotate_key(req: dict, _auth: str = Depends(require_admin)):
    """Y26: Enterprise kullanicinin API key'ini yeniler (eski key gecersiz olur).
    Girdi: user_id. Cikti: yeni api_key (bir kez gorunur)."""
    user_id = req.get("user_id") or ""
    try:
        uuid.UUID(user_id)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(status_code=400, detail="user_id UUID olmali")
    engine = get_engine()
    with engine.begin() as conn:
        row = (
            conn.execute(
                text("SELECT email, tier, status FROM users WHERE user_id = :u"),
                {"u": user_id},
            )
            .mappings()
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail="kullanici bulunamadi")
        if row["tier"] != "enterprise":
            raise HTTPException(
                status_code=400, detail="key rotasyonu yalnizca enterprise tier icin"
            )
        yeni = (
            "ent_"
            + hmac.new(
                _DASH_SECRET.encode(),
                f"{user_id}:{_time.time()}".encode(),
                hashlib.sha256,
            ).hexdigest()[:32]
        )
        conn.execute(
            text(
                "UPDATE users SET api_key = :k, updated_at = CURRENT_TIMESTAMP WHERE user_id = :u"
            ),
            {"k": yeni, "u": user_id},
        )
    return {"ok": True, "api_key": yeni}


@admin_cache(ttl=300)
@app.get("/api/admin/categories")
def api_admin_categories(_auth: str = Depends(require_admin)):
    # Cache TTL: 300s
    """Y25: Urun katalogu yonetimi - tum kategoriler (aktif + pasif)."""
    engine = get_engine()
    with engine.connect() as conn:
        rows = (
            conn.execute(
                text(
                    "SELECT category_id, code, label_tr, nace_group, description, active, created_at "
                    "FROM product_categories ORDER BY nace_group, code"
                )
            )
            .mappings()
            .all()
        )
    return {"items": [dict(r) for r in rows]}


@app.post("/api/admin/categories")
def api_admin_categories_save(req: dict, _auth: str = Depends(require_admin)):
    """Kategori ekle/guncelle. category_id varsa guncelle, yoksa yeni olustur.
    active=false ile pasiflesirme (kayit silinmez, kayit formunda kaybolur)."""
    code = (req.get("code") or "").strip().upper()
    label_tr = (req.get("label_tr") or "").strip()
    nace_group = (req.get("nace_group") or "").strip() or None
    description = (req.get("description") or "").strip() or None
    active = bool(req.get("active", True))
    category_id = req.get("category_id") or None
    if not code or not label_tr:
        raise HTTPException(status_code=400, detail="code ve label_tr zorunlu")
    if len(code) > 20:
        raise HTTPException(status_code=400, detail="code en fazla 20 karakter")
    if nace_group and not nace_group.isdigit():
        raise HTTPException(
            status_code=400, detail="nace_group 2 haneli sayi olmali (orn. 29)"
        )
    engine = get_engine()
    with engine.begin() as conn:
        if category_id:
            try:
                uuid.UUID(str(category_id))
            except (ValueError, AttributeError, TypeError):
                raise HTTPException(status_code=400, detail="category_id UUID olmali")
            row = (
                conn.execute(
                    text("SELECT code FROM product_categories WHERE category_id = :c"),
                    {"c": category_id},
                )
                .mappings()
                .first()
            )
            if not row:
                raise HTTPException(status_code=404, detail="kategori bulunamadi")
            if row["code"] != code:
                dup = conn.execute(
                    text("SELECT 1 FROM product_categories WHERE code = :k"),
                    {"k": code},
                ).first()
                if dup:
                    raise HTTPException(status_code=409, detail="Bu code zaten kayitli")
            conn.execute(
                text(
                    "UPDATE product_categories SET code=:k, label_tr=:l, nace_group=:n, "
                    "description=:d, active=:a WHERE category_id=:c"
                ),
                {
                    "k": code,
                    "l": label_tr,
                    "n": nace_group,
                    "d": description,
                    "a": active,
                    "c": category_id,
                },
            )
            return {"ok": True, "updated": True}
        dup = conn.execute(
            text("SELECT 1 FROM product_categories WHERE code = :k"), {"k": code}
        ).first()
        if dup:
            raise HTTPException(status_code=409, detail="Bu code zaten kayitli")
        conn.execute(
            text(
                "INSERT INTO product_categories (code, label_tr, nace_group, description, active) "
                "VALUES (:k, :l, :n, :d, :a)"
            ),
            {"k": code, "l": label_tr, "n": nace_group, "d": description, "a": active},
        )
    return {"ok": True, "created": True}


@app.post("/api/admin/kvkk-mode")
def api_admin_kvkk_mode(req: dict, _auth: str = Depends(require_admin)):
   """D-207: Admin KVKK mode toggle (strict ↔ lenient).
   
   strict: KVKK kesinlikle uygulanır (yasak alanlar maskelenir)
   lenient: Admin riski alıp kısıtlı alanları açar (yasak kalır)
   
   İstek: {mode: 'strict' | 'lenient', reason: str}
   Cevap: {ok: bool, previous_mode: str, new_mode: str, changed_at: str}
   """
   mode = (req.get("mode") or "").strip().lower()
   reason = (req.get("reason") or "").strip()
   
   if mode not in ("strict", "lenient"):
       raise HTTPException(status_code=400, detail="mode 'strict' veya 'lenient' olmalı")
   if not reason or len(reason) < 3:
       raise HTTPException(status_code=400, detail="reason en az 3 karakter olmalı")
   
   # Admin ID'sini token'dan al
   auth_header = req.get("_auth_header") or ""
   admin_id = "system"  # ponytail: Token parsing opsiyonel; system default
   
   engine = get_engine()
   
   # Mevcut mode'u oku
   previous_mode = "strict"  # default
   with engine.connect() as conn:
       row = conn.execute(
           text("SELECT mode FROM admin_kvkk_mode WHERE effective_to IS NULL ORDER BY changed_at DESC LIMIT 1")
       ).mappings().first()
       if row:
           previous_mode = row["mode"]
   
   # Eğer zaten aynı mode'daysa, değişiklik yapma
   if mode == previous_mode:
       return {
           "ok": True,
           "previous_mode": previous_mode,
           "new_mode": mode,
           "changed_at": datetime.now().isoformat(),
           "message": "Mevcut mode ile aynı"
       }
   
   # Eski mod'ü sonlandır ve yenisini ekle
   now = datetime.now().isoformat()
   try:
       with engine.begin() as conn:
           # Mevcut modu sonlandır
           conn.execute(
               text("UPDATE admin_kvkk_mode SET effective_to = :now WHERE effective_to IS NULL"),
               {"now": now}
           )
           # Yeni modu ekle
           conn.execute(
               text("""
                   INSERT INTO admin_kvkk_mode (admin_id, mode, changed_at, reason, effective_to)
                   VALUES (:admin_id, :mode, :changed_at, :reason, NULL)
               """),
               {
                   "admin_id": admin_id,
                   "mode": mode,
                   "changed_at": now,
                   "reason": reason,
               }
           )
       # Cache'i temizle
       cache_set("kvkk_admin_mode", mode)
       return {
           "ok": True,
           "previous_mode": previous_mode,
           "new_mode": mode,
           "changed_at": now
       }
   except Exception as e:
           raise HTTPException(status_code=500, detail=f"Mode değiştirilemedi: {str(e)}")


# UI-ADMIN-FEATURE-FLAG-25: Feature Flag Yönetim Endpoint
@app.post("/api/admin/feature-flags")
def admin_feature_flag_toggle(
    req: dict,
    request: Request,
    _auth: str = Depends(require_admin_role)
) -> dict:
    """Feature flag toggle: {flag_name: str, new_value: bool} -> {ok, previous, new, changed_at}.
    
    Admin role required. Audit log yazılır.
    """
    try:
        flag_name = (req.get("flag_name") or "").strip()
        new_value = bool(req.get("new_value"))
        if not flag_name:
            raise HTTPException(status_code=400, detail="flag_name zorunlu")
        
        # Mevcut değer
        flags = _get_feature_flags()
        previous = flags.get(flag_name, False)
        
        if previous == new_value:
            return {
                "ok": True,
                "previous": previous,
                "new": new_value,
                "changed_at": datetime.now().isoformat(),
                "message": "Değer zaten aynı"
            }
        
        # Güncelle
        flags[flag_name] = new_value
        _save_feature_flags(flags)
        
        # Audit log
        admin_id = _get_admin_id_from_request(request)
        _log_feature_flag_change(admin_id, flag_name, previous, new_value)
        
        return {
            "ok": True,
            "previous": previous,
            "new": new_value,
            "changed_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature flag değiştirilemedi: {str(e)}")


def _get_feature_flags() -> dict[str, bool]:
    """Feature flag'leri session state'ten oku."""
    try:
        import streamlit as st
        return dict(st.session_state.get("_feature_flags", {}))
    except Exception:
        return {}


def _get_plan_field_visibility(company_id: str) -> dict:
    """plan_field_group tablosundan paket bazlı alan görünürlüğü okur (Layer 2)."""""
    engine = get_engine()
    plan_field_visibility = {}
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT pf.field_group, pf.visibility
                FROM plan_field_group pf
                JOIN companies c ON c.plan_id = pf.plan_id
                WHERE c.company_id = :cid AND pf.effective_to IS NULL
            """), {"cid": company_id}).mappings().all()
            for row in rows:
                plan_field_visibility[row["field_group"]] = row["visibility"]
    except Exception:
        pass
    return plan_field_visibility


def _save_feature_flags(flags: dict[str, bool]) -> None:
    """Feature flag'leri session state'e yaz."""
    try:
        import streamlit as st
        st.session_state["_feature_flags"] = dict(flags)
    except Exception:
        pass


def _get_admin_id_from_request(request: Request) -> str:
    """Request'ten admin ID al."""
    try:
        session = _get_session(request)
        if session and session.user:
            return session.user.email
    except Exception:
        pass
    return "unknown"


def _log_feature_flag_change(admin_id: str, flag_name: str, old_value: bool, new_value: bool) -> None:
    """Feature flag değişikliğini audit log'a yaz."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO admin_audit_log (admin_id, action, target, old_value, new_value, changed_at)
                    VALUES (:admin_id, 'feature_flag_toggle', :flag_name, :old_val, :new_val, CURRENT_TIMESTAMP)
                """),
                {
                    "admin_id": admin_id,
                    "flag_name": flag_name,
                    "old_val": str(old_value).lower(),
                    "new_val": str(new_value).lower(),
                },
            )
            conn.commit()
    except Exception as e:
        print(f"[FEATURE-FLAG-AUDIT] Log yazılamadı: {e}")


@app.get("/api/dashboard", response_class=HTMLResponse)
def serve_dashboard(_auth: str = Depends(require_api_key)) -> HTMLResponse:
    index = WEB_DIR / "index.html"
    if not index.exists():
        return HTMLResponse("<h1>Dashboard not found</h1>", status_code=404)
    return HTMLResponse(index.read_text(encoding="utf-8"))


@admin_cache(ttl=30)
@app.get("/api/performance")
def performance_report(_auth: str = Depends(require_api_key)) -> dict:
    # Cache TTL: 30s
    global _DB_TIME_MS, _QUERY_COUNT, _CACHE_HITS, _CACHE_MISSES
    return {
        "db_time_ms": round(_DB_TIME_MS, 2),
        "query_count": _QUERY_COUNT,
        "cache_hits": _CACHE_HITS,
        "cache_misses": _CACHE_MISSES,
        "cache_hit_rate": round(_CACHE_HITS / max(1, _CACHE_HITS + _CACHE_MISSES), 4),
        "slow_queries": [q for q in _QUERY_TIMES if q["ms"] > 100],
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/quality-trend")
def api_quality_trend(_auth: str = Depends(require_api_key)) -> list[dict]:
    """Kalite skoru dagilimi (bucket bazli) - SQLite/PostgreSQL uyumlu."""
    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT CASE
                WHEN data_quality_score >= 80 THEN '80-100'
                WHEN data_quality_score >= 60 THEN '60-79'
                WHEN data_quality_score >= 40 THEN '40-59'
                WHEN data_quality_score >= 20 THEN '20-39'
                ELSE '0-19'
            END as bucket, COUNT(*) as cnt
            FROM companies
            WHERE is_ankara=TRUE AND is_osb_member=TRUE
            GROUP BY 1
            ORDER BY 1 DESC
        """)).mappings().all()
        return [dict(r) for r in rows] if rows else []


@app.get("/api/nace-distribution")
def api_nace_distribution(
    limit: int = 20, _auth: str = Depends(require_api_key)
) -> list[dict]:
    """NACE kodu x firma sayisi (top N) - nace_codes tablosu olmadan."""
    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        rows = (
            conn.execute(
                text("""
            SELECT c.nace_code, COUNT(*) as cnt
            FROM companies c
            WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE AND c.nace_code IS NOT NULL AND c.nace_code != ''
            GROUP BY c.nace_code
            ORDER BY cnt DESC
            LIMIT :lim
        """),
                {"lim": limit},
            )
            .mappings()
            .all()
        )
        return [dict(r) for r in rows] if rows else []


@app.get("/api/sources")
def api_sources(_auth: str = Depends(require_api_key)) -> list[dict]:
    """Veri kaynaklari durumu - PostgreSQL (sources + source_records tablolari)."""
    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT s.source_name, s.source_type, s.url,
                   COUNT(sr.source_record_id) as record_count,
                   MAX(sr.collected_at) as last_scrape
            FROM sources s
            LEFT JOIN source_records sr ON sr.source_id = s.source_id
            GROUP BY s.source_id, s.source_name, s.source_type, s.url
            ORDER BY record_count DESC
        """)).mappings().all()
        return [dict(r) for r in rows] if rows else []


@app.get("/api/company/{company_id}")
def api_company_detail(
    company_id: str, mask: int = 0, _auth: str = Depends(require_api_key)
) -> dict:
    """Tek firma detayi. KVKK: 2-katman görünürlük (Layer 1: kod sınıfı, Layer 2: paket×grup tablo).
    D-205: Seçici SELECT — sadece açık + yarı-açık alanlar. Yasak meta alanları hiç seçme."""
    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        # Seçici SELECT (SELECT c.* yerine) — meta alanları dışla
        # ponytail: Layer 2 tablo (plan_field_group) paket bazında kolon filtresi yapmayacak;
        #           API seviyesinde statik whitelist yeterli. Paket görünürlüğü maskeleme'de (A3 apply_kvkk_mask).
        sql = text("""
            SELECT c.company_id, c.legal_name, c.trade_name, c.company_registration_number,
                   c.foundation_year, c.primary_phone, c.primary_email, c.website,
                   c.phone_validity_status, c.email_validity_status, c.address, c.city,
                   c.province, c.country, c.zip_code, c.website_exists, c.domain_valid,
                   c.digital_presence, c.annual_turnover, c.employee_count, c.turnover_range,
                   c.employee_range, c.nace_code, c.industry_code, c.sector, c.subsector,
                   c.manufacturing, c.created_at, c.updated_at
            FROM companies c WHERE c.company_id = :cid
        """)
        r = (
            conn.execute(sql, {"cid": company_id})
            .mappings()
            .first()
        )
        if r:
            row = dict(r)
            for k, v in row.items():
                if isinstance(v, (float,)) and v is not None:
                    row[k] = float(v)
            row = normalize_company(row)
            # Admin modu: strict (default) | lenient (mask=0 dışı)
            admin_mode = "lenient" if mask == 1 else "strict"
            if _mask_active(mask):
                # Layer 2 plan_field_visibility from DB
                plan_field_visibility = _get_plan_field_visibility(company_id)
                row = apply_kvkk_mask(row, admin_mode=admin_mode, plan_field_visibility=plan_field_visibility)
            return row
        return {}



# ── P7-19b: SSE cache (dashboard verisi) ──
_SSE_LAST_DATA: dict[str, Any] = {}


def _fetch_dashboard_data(limit: int = 10) -> dict:
    """P7-15/P7-19b ortak: Signal Dashboard verisini DB'den çeker."""
    engine = get_engine()
    now_iso = datetime.utcnow().isoformat()
    out: dict[str, Any] = {
        "signal_type_counts": {},
        "total_active_signals": 0,
        "scored_companies": 0,
        "top_growth": [],
        "top_investment": [],
        "top_risk": [],
        "hiring_trends": {},
        "recent_signals": [],
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }

    def _safe_rows(sql, params=None):
        try:
            with engine.connect() as conn:
                rows = conn.execute(text(sql), params or {}).mappings().all()
                return [dict(r) for r in rows]
        except Exception:
            return []

    rows = _safe_rows("""
        SELECT signal_type, COUNT(*) AS cnt
        FROM company_signals
        WHERE valid_until IS NULL OR valid_until > :now
        GROUP BY signal_type ORDER BY cnt DESC
    """, {"now": now_iso})
    total = 0
    for r in rows:
        out["signal_type_counts"][r["signal_type"]] = r["cnt"]
        total += r["cnt"]
    out["total_active_signals"] = total

    rows = _safe_rows("SELECT COUNT(*) AS cnt FROM company_intelligence_scores")
    out["scored_companies"] = rows[0]["cnt"] if rows else 0

    top_sql = """
        SELECT s.company_id, c.legal_name, s.{field} AS score,
               s.hiring_trend, s.overall_confidence, s.signal_count_30d,
               s.updated_at
        FROM company_intelligence_scores s
        LEFT JOIN companies c ON c.company_id = s.company_id
        ORDER BY s.{field} DESC LIMIT :lim
    """
    out["top_growth"] = _safe_rows(top_sql.format(field="growth_score"), {"lim": limit})
    out["top_investment"] = _safe_rows(
        top_sql.format(field="investment_signal_score"), {"lim": limit}
    )
    out["top_risk"] = _safe_rows(top_sql.format(field="risk_score"), {"lim": limit})

    rows = _safe_rows("""
        SELECT hiring_trend, COUNT(*) AS cnt
        FROM company_intelligence_scores
        GROUP BY hiring_trend ORDER BY cnt DESC
    """)
    out["hiring_trends"] = {r["hiring_trend"]: r["cnt"] for r in rows}

    rows = _safe_rows("""
        SELECT cs.company_id, c.legal_name, cs.signal_type, cs.signal_subtype,
               cs.score, cs.confidence, cs.detected_at, cs.valid_until
        FROM company_signals cs
        LEFT JOIN companies c ON c.company_id = cs.company_id
        WHERE cs.valid_until IS NULL OR cs.valid_until > :now
        ORDER BY cs.detected_at DESC LIMIT :lim
    """, {"now": now_iso, "lim": min(limit, 50)})
    out["recent_signals"] = rows
    return out


@app.get("/api/intelligence/dashboard")
def api_intelligence_dashboard(
    limit: int = 10, _auth: str = Depends(require_api_key)
) -> dict:
    """P7-15: Signal Dashboard aggregation."""
    global _SSE_LAST_DATA
    out = _fetch_dashboard_data(limit=limit)
    _SSE_LAST_DATA = out.copy()
    return out


@app.get("/api/intelligence/dashboard/stream")
async def api_intelligence_dashboard_stream(_auth: str = Depends(require_api_key)) -> StreamingResponse:
    """P7-19b: SSE stream - müşteri paneli için gerçek zamanlı sinyal güncellemeleri.

    Her 5 saniyede bir DB'den taze veri çeker ve push eder.
    EventSource (browser) tarafından consumed edilir.
    """
    async def event_generator():
        global _SSE_LAST_DATA
        # İlk veri: cache varsa onu, yoksa DB'den çek
        try:
            data = _SSE_LAST_DATA.copy() if _SSE_LAST_DATA else _fetch_dashboard_data(limit=8)
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        except Exception:
            yield f"data: {json.dumps({'generated_at': datetime.utcnow().isoformat(), 'total_active_signals': 0}, ensure_ascii=False)}\n\n"
        while True:
            try:
                await asyncio.sleep(5)
                # Her döngüde taze veri çek ve cache'i güncelle
                data = _fetch_dashboard_data(limit=8)
                _SSE_LAST_DATA = data.copy()
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1)
                continue

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ============================================================
# API-ADMIN-MFA-26: Multi-Factor Authentication (MFA) Endpoints
# ============================================================

def _generate_backup_codes(count: int = 8) -> list[str]:
    """8 tane 4 karakterli backup kodu üret (base32, uppercase)."""
    import secrets
    codes = []
    for _ in range(count):
        # 4 karakter = 20 bits = 4 base32 chars
        code = secrets.token_bytes(3).hex()[:4].upper()
        codes.append(code)
    return codes


def _hash_backup_codes(codes: list[str]) -> str:
    """Backup kodlarını SHA256 ile hashle (JSON array string olarak sakla)."""
    import hashlib
    import json
    hashes = [hashlib.sha256(code.encode()).hexdigest() for code in codes]
    return json.dumps(hashes)


def _verify_backup_code(codes_json: str, input_code: str) -> bool:
    """Girilen kodu hashle ve saklı hashlerle karşılaştır."""
    import hashlib
    import json
    input_hash = hashlib.sha256(input_code.upper().encode()).hexdigest()
    try:
        stored_hashes = json.loads(codes_json)
        return input_hash in stored_hashes
    except (json.JSONDecodeError, TypeError):
        return False


@app.post("/api/admin/mfa/setup")
def api_admin_mfa_setup(
    req: dict,
    request: Request,
    _auth: str = Depends(require_admin_role)
):
    """API-ADMIN-MFA-26: MFA setup başlat.
    
    Request: {}
    Response: {secret_key, qr_code_base64, mfa_token, expires_at}
    """
    try:
        # Admin email'i session'dan al
        session = _get_session(request)
        if not session or not session.user:
            raise HTTPException(status_code=401, detail="Oturum geçersiz")
        
        admin_email = session.user.email
        admin_id = session.user.user_id
        
        # Zaten MFA aktif mi kontrol et
        engine = get_engine()
        with engine.connect() as conn:
            existing = conn.execute(
                text("SELECT enabled FROM admin_mfa WHERE admin_id = :aid"),
                {"aid": admin_id}
            ).mappings().first()
            
            if existing and existing["enabled"]:
                raise HTTPException(status_code=400, detail="MFA zaten aktif. Önce devre dışı bırakın.")
        
        # TOTP secret üret (base32)
        secret_key = pyotp.random_base32()
        
        # MFA token üret (1 dakika geçerli)
        import secrets
        mfa_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=1)
        
        # QR kod oluştur
        totp_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=admin_email,
            issuer_name="Huginn Data Insights"
        )
        qr = qrcode.make(totp_uri)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        qr_base64 = base64.b64encode(buf.getvalue()).decode()
        
        # Setup token'ı geçici tabloya kaydet
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO admin_mfa_setup_tokens 
                    (admin_id, secret_key, mfa_token, expires_at)
                    VALUES (:aid, :secret, :token, :exp)
                """),
                {
                    "aid": admin_id,
                    "secret": secret_key,
                    "token": mfa_token,
                    "exp": expires_at
                }
            )
        
        return {
            "ok": True,
            "secret_key": secret_key,
            "qr_code_base64": qr_base64,
            "mfa_token": mfa_token,
            "expires_at": expires_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MFA setup başlatılamadı: {str(e)}")


@app.post("/api/admin/mfa/verify")
def api_admin_mfa_verify(
    req: dict,
    _auth: str = Depends(require_admin_role)
):
    """API-ADMIN-MFA-26: MFA doğrulama ve aktifleştirme.
    
    Request: {mfa_token, code}
    Response: {ok, message, backup_codes}
    """
    try:
        mfa_token = (req.get("mfa_token") or "").strip()
        code = (req.get("code") or "").strip()
        
        if not mfa_token or not code:
            raise HTTPException(status_code=400, detail="mfa_token ve code zorunlu")
        
        # Session'dan admin ID al
        session_data = req.get("session")  # This is a placeholder
        # In real implementation, we'd get this from the request context
        
        # For now, extract from request headers or body
        # This is simplified - in production use proper auth
        
        engine = get_engine()
        
        # Setup token'ı doğrula
        with engine.connect() as conn:
            setup = conn.execute(
                text("""
                    SELECT admin_id, secret_key 
                    FROM admin_mfa_setup_tokens 
                    WHERE mfa_token = :token AND used = FALSE AND expires_at > NOW()
                """),
                {"token": mfa_token}
            ).mappings().first()
            
            if not setup:
                raise HTTPException(status_code=400, detail="Geçersiz veya süresi dolmuş MFA token")
            
            admin_id = setup["admin_id"]
            secret_key = setup["secret_key"]
        
        # TOTP kodu doğrula
        totp = pyotp.TOTP(secret_key)
        if not totp.verify(code, valid_window=1):
            raise HTTPException(status_code=400, detail="Geçersiz MFA kodu")
        
        # Backup codes üret
        backup_codes = _generate_backup_codes(8)
        backup_codes_hash = _hash_backup_codes(backup_codes)
        
        # MFA kaydını oluştur
        with engine.begin() as conn:
            # Admin MFA kaydını oluştur/güncelle
            conn.execute(
                text("""
                    INSERT INTO admin_mfa (admin_id, secret_key, enabled, backup_codes, created_at)
                    VALUES (:aid, :secret, TRUE, :backup, NOW())
                    ON CONFLICT (admin_id) DO UPDATE SET
                        secret_key = EXCLUDED.secret_key,
                        enabled = TRUE,
                        backup_codes = EXCLUDED.backup_codes,
                        updated_at = NOW()
                """),
                {
                    "aid": setup["admin_id"],
                    "secret": secret_key,
                    "backup": backup_codes_hash
                }
            )
            
            # Setup token'ı kullanılmış olarak işaretle
            conn.execute(
                text("UPDATE admin_mfa_setup_tokens SET used = TRUE WHERE mfa_token = :token"),
                {"token": mfa_token}
            )
        
        return {
            "ok": True,
            "message": "MFA başarıyla aktifleştirildi",
            "backup_codes": backup_codes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MFA doğrulama hatası: {str(e)}")


@app.post("/api/admin/mfa/disable")
def api_admin_mfa_disable(
    req: dict,
    _auth: str = Depends(require_admin_role)
):
    """MFA devre dışı bırak (mevcut şifre gerekli)."""
    try:
        # Password ve email iste
        password = req.get("password") or ""
        if not password:
            raise HTTPException(status_code=400, detail="Mevcut şifre zorunlu")
        
        # Admin email'i session'dan al
        session_data = req.get("session")  # Placeholder
        # In practice, get from request context
        
        # For now, require email in request
        email = req.get("email") or ""
        if not email:
            raise HTTPException(status_code=400, detail="Email zorunlu")
        
        # Şifre doğrula
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT password_hash FROM users WHERE email = :e AND role = 'admin'"),
                {"e": email}
            ).mappings().first()
            
            if not row or not _verify_password(password, row["password_hash"]):
                raise HTTPException(status_code=401, detail="Geçersiz şifre")
            
            # MFA devre dışı bırak
            conn.execute(
                text("UPDATE admin_mfa SET enabled = FALSE, updated_at = NOW() WHERE admin_id = (SELECT user_id FROM users WHERE email = :e)"),
                {"e": email}
            )
        
        return {"ok": True, "message": "MFA devre dışı bırakıldı"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MFA devre dışı bırakma hatası: {str(e)}")


@app.post("/api/admin/mfa/backup-codes")
def api_admin_mfa_backup_codes(
    req: dict,
    _auth: str = Depends(require_admin_role)
):
    """Backup codes yeniden üret."""
    try:
        # Admin email
        email = req.get("email") or ""
        if not email:
            raise HTTPException(status_code=400, detail="Email zorunlu")
        
        # MFA aktif mi kontrol et
        engine = get_engine()
        with engine.connect() as conn:
            mfa = conn.execute(
                text("SELECT admin_id, enabled FROM admin_mfa WHERE admin_id = (SELECT user_id FROM users WHERE email = :e)"),
                {"e": req.get("email", "")}
            ).mappings().first()
            
            if not mfa or not mfa["enabled"]:
                raise HTTPException(status_code=400, detail="MFA aktif değil")
        
        # Yeni backup codes üret
        backup_codes = _generate_backup_codes(8)
        backup_codes_hash = _hash_backup_codes(backup_codes)
        
        # Kaydet
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE admin_mfa SET backup_codes = :backup, updated_at = NOW() WHERE admin_id = :aid"),
                {"backup": backup_codes_hash, "aid": mfa["admin_id"]}
            )
        
        return {
            "ok": True,
            "message": "Yeni backup kodları üretildi",
            "backup_codes": backup_codes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup codes hatası: {str(e)}")


@app.post("/api/admin/login-mfa")
def api_admin_login_mfa(req: dict, request: Request):
    """2. adım MFA login: {mfa_token, code} -> auth token."""
    try:
        mfa_token = (req.get("mfa_token") or "").strip()
        code = (req.get("code") or "").strip()
        
        if not mfa_token or not code:
            raise HTTPException(status_code=400, detail="mfa_token ve code zorunlu")
        
        engine = get_engine()
        
        # MFA token'ı doğrula
        with engine.connect() as conn:
            setup = conn.execute(
                text("""
                    SELECT admin_id 
                    FROM admin_mfa_setup_tokens 
                    WHERE mfa_token = :token AND used = FALSE AND expires_at > NOW()
                """),
                {"token": mfa_token}
            ).mappings().first()
            
            if not setup:
                raise HTTPException(status_code=400, detail="Geçersiz veya süresi dolmuş MFA token")
            
            admin_id = setup["admin_id"]
            
            # Admin email al
            admin = conn.execute(
                text("SELECT email FROM users WHERE user_id = :aid"),
                {"aid": admin_id}
            ).mappings().first()
            
            if not admin:
                raise HTTPException(status_code=404, detail="Admin bulunamadı")
            
            email = admin["email"]
        
        # MFA kaydını bul ve TOTP doğrula
        with engine.connect() as conn:
            mfa = conn.execute(
                text("SELECT secret_key FROM admin_mfa WHERE admin_id = :aid AND enabled = TRUE"),
                {"aid": admin_id}
            ).mappings().first()
            
            if not mfa:
                raise HTTPException(status_code=400, detail="MFA aktif değil")
            
            secret_key = mfa["secret_key"]
        
        # TOTP doğrula
        totp = pyotp.TOTP(secret_key)
        if not totp.verify(code, valid_window=1):
            raise HTTPException(status_code=401, detail="Geçersiz MFA kodu")
        
        # MFA token'ı kullanılmış olarak işaretle
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE admin_mfa_setup_tokens SET used = TRUE WHERE mfa_token = :token"),
                {"token": mfa_token}
            )
        
        # Başarılı - token üret
        token = _user_token(email)
        aktivite_yaz(user_id=email, olay_tipi="giris", basarili=True, request=request)
        
        return {"token": token}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MFA login hatası: {str(e)}")


@app.get("/api/admin/mfa/status")
def api_admin_mfa_status(
    _auth: str = Depends(require_admin_role)
):
    """MFA durumu sorgula."""
    try:
        # Placeholder - in practice get from session
        email = "admin@huginn.local"  # placeholder
        
        engine = get_engine()
        with engine.connect() as conn:
            mfa = conn.execute(
                text("""
                    SELECT enabled, created_at, last_used_at, backup_codes IS NOT NULL as has_backup
                    FROM admin_mfa 
                    WHERE admin_id = (SELECT user_id FROM users WHERE email = :e)
                """),
                {"e": email}
            ).mappings().first()
            
            if not mfa:
                return {"enabled": False}
            
            return {
                "enabled": mfa["enabled"],
                "created_at": str(mfa["created_at"]) if mfa["created_at"] else None,
                "last_used_at": str(mfa["last_used_at"]) if mfa["last_used_at"] else None,
                "has_backup_codes": mfa["has_backup"]
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MFA status hatası: {str(e)}")
