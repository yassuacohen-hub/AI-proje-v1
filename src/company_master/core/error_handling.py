# -*- coding: utf-8 -*-
"""Error Handling & Logging Module (UTKU-03)

Structured logging with JSON output, PII masking, request context enrichment,
and production-ready configuration for ELK/Datadog integration.
"""

import json
import logging
import logging.handlers
import os
import re
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Dict, Optional, Union

try:
    import orjson as json_lib
    _ORJSON_VAR = True
except ImportError:
    import json as json_lib
    _ORJSON_VAR = False

# ============================================================
# Constants
# ============================================================

# PII patterns to mask
PII_PATTERNS = [
    (re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'), '[PHONE]'),  # Phone
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]'),  # Email
    (re.compile(r'\b\d{11}\b'), '[TCKN]'),  # Turkish TCKN
    (re.compile(r'\b\d{16}\b'), '[CARD]'),  # Credit card
    (re.compile(r'(?i)(password|secret|token|api_key|apikey)\s*[:=]\s*\S+'), '[SECRET]'),  # Secrets
    (re.compile(r'(?i)(authorization|bearer)\s+[A-Za-z0-9\-_\.]+'), '[TOKEN]'),  # Auth tokens
]

# Log levels
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

# Default log format
DEFAULT_LOG_FORMAT = '%(message)s'

# ============================================================
# Sensitive Data Masking
# ============================================================

# Dict anahtarlarinda gecen secret isimleri -> deger tamamen maskelenir
SENSITIVE_KEYS = re.compile(
    r'(?i)(pass(word)?|secret|token|api[_-]?key|apikey|auth|credential|private[_-]?key)'
)

MASK = '***'


def mask_sensitive(data: Union[str, Dict, Any]) -> Union[str, Dict, Any]:
    """Mask sensitive data (PII, secrets) in string or dict.

    Args:
        data: String, dict, list, or any JSON-serializable object

    Returns:
        Masked version of the input
    """
    if isinstance(data, str):
        result = data
        for pattern, replacement in PII_PATTERNS:
            result = pattern.sub(replacement, result)
        return result

    elif isinstance(data, dict):
        result = {}
        for k, v in data.items():
            # Anahtar adi secret gosteriyorsa degerin tamamini maskele
            if isinstance(k, str) and SENSITIVE_KEYS.search(k):
                result[k] = MASK
            elif isinstance(v, str):
                masked = v
                for pattern, replacement in PII_PATTERNS:
                    masked = pattern.sub(replacement, masked)
                result[k] = masked
            elif isinstance(v, (dict, list)):
                result[k] = mask_sensitive(v)
            else:
                result[k] = v
        return result

    elif isinstance(data, list):
        return [mask_sensitive(item) for item in data]

    return data


# ============================================================
# Structured JSON Formatter
# ============================================================

class JSONFormatter(logging.Formatter):
    """JSON log formatter for ELK/Datadog compatibility."""

    #: LogRecord'un JSON'a sizmamasi icin elenmesi gereken standart alanlar
    RESERVED = frozenset({
        'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
        'funcName', 'levelname', 'levelno', 'lineno', 'message', 'module',
        'msecs', 'msg', 'name', 'pathname', 'process', 'processName',
        'relativeCreated', 'stack_info', 'taskName', 'thread', 'threadName',
    })

    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra

    @staticmethod
    def _dump(payload: Dict[str, Any]) -> str:
        """orjson varsa onu kullan (hizli), yoksa stdlib json.

        orjson `ensure_ascii` ve `default` parametrelerini desteklemez;
        bu yuzden her iki kutuphane icin ayri dal kullanilir.
        """
        if _ORJSON_VAR:
            return json_lib.dumps(payload, default=str).decode('utf-8')
        return json_lib.dumps(payload, default=str, ensure_ascii=False)

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Istisna bilgisi
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            log_entry['exception'] = {
                'type': exc_type.__name__ if exc_type else None,
                'message': str(exc_value) if exc_value else None,
                'traceback': ''.join(
                    logging.Formatter().formatException(record.exc_info)
                ),
            }
        if record.stack_info:
            log_entry['stack'] = self.formatStack(record.stack_info)

        # Context enrichment + extra alanlar
        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in self.RESERVED
        }
        if extra_fields:
            log_entry.update(mask_sensitive(extra_fields))

        return self._dump(log_entry)


# ============================================================
# Request Context Enrichment
# ============================================================

class LogContext:
    """Context manager for request-scoped log enrichment."""

    def __init__(self, request_id: Optional[str] = None, user_id: Optional[str] = None,
                 trace_id: Optional[str] = None, **extra):
        self.request_id = request_id or str(uuid.uuid4())[:8]
        self.user_id = user_id
        self.trace_id = trace_id or str(uuid.uuid4())
        self.extra = extra
        self._old_factory = logging.getLogRecordFactory()

    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self._old_factory(*args, **kwargs)
            record.request_id = self.request_id
            record.trace_id = self.trace_id
            if self.user_id:
                record.user_id = self.user_id
            for k, v in self.extra.items():
                setattr(record, k, v)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self._old_factory)


# Thread-local context storage
_thread_local = None
try:
    import threading
    _thread_local = threading.local()
except ImportError:
    pass


def set_log_context(request_id: Optional[str] = None, user_id: Optional[str] = None,
                    trace_id: Optional[str] = None, **extra):
    """Set request-scoped log context (thread-local)."""
    if _thread_local is not None:
        _thread_local.request_id = request_id or str(uuid.uuid4())[:8]
        _thread_local.user_id = user_id
        _thread_local.trace_id = trace_id or str(uuid.uuid4())
        _thread_local._extra = dict(extra)


def clear_log_context():
    """Clear thread-local log context."""
    if _thread_local is not None:
        for attr in ('request_id', 'user_id', 'trace_id'):
            if hasattr(_thread_local, attr):
                delattr(_thread_local, attr)
        if hasattr(_thread_local, '_extra'):
            delattr(_thread_local, '_extra')


def get_log_context() -> Dict[str, Any]:
    """Get current thread-local log context."""
    if _thread_local is None:
        return {}
    context = {}
    for attr in ('request_id', 'user_id', 'trace_id'):
        if hasattr(_thread_local, attr):
            value = getattr(_thread_local, attr)
            if value is not None:
                context[attr] = value
    # set_log_context(**extra) ile eklenen ozel alanlar
    for key, value in getattr(_thread_local, '_extra', {}).items():
        context[key] = value
    return context


# ============================================================
# Logging Setup
# ============================================================

def setup_logging(
    level: str = 'INFO',
    json_format: bool = True,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_output: bool = True,
) -> logging.Logger:
    """Configure application-wide logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON formatter if True
        log_file: Optional file path for file output
        max_bytes: Max file size before rotation
        backup_count: Number of backup files to keep
        console_output: Also output to stdout

    Returns:
        Root logger instance
    """
    level = LOG_LEVELS.get(level.upper(), logging.INFO)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)

    # File handler with rotation
    if log_file:
        dizin = os.path.dirname(log_file)
        if dizin:
            os.makedirs(dizin, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)

    # Prevent propagation to root (avoid duplicate logs)
    logging.getLogger('uvicorn').propagate = False
    logging.getLogger('uvicorn.access').propagate = False
    logging.getLogger('fastapi').propagate = False

    root_logger.info('Logging configured', extra={
        'level': level,
        'json_format': json_format,
        'log_file': log_file,
    })

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get module-level logger with context enrichment."""
    logger = logging.getLogger(name)

    # Add context filter if not already added
    if not any(isinstance(h, _ContextFilter) for h in logger.filters):
        logger.addFilter(_ContextFilter())

    return logger


class _ContextFilter(logging.Filter):
    """Filter to add thread-local context to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        context = get_log_context()
        for key, value in context.items():
            setattr(record, key, value)
        return True


# ============================================================
# Exception Handling
# ============================================================

def log_exception(logger: logging.Logger, exc: Exception,
                  context: Optional[Dict] = None, level: int = logging.ERROR):
    """Log exception with full context."""
    extra = {'exception_type': type(exc).__name__}
    if context:
        extra.update(context)
    logger.log(level, str(exc), exc_info=True, extra=extra)


def handle_exception(logger: Optional[logging.Logger] = None):
    """Decorator to catch and log exceptions in functions."""
    if logger is None:
        logger = logging.getLogger(__name__)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 'args'/'kwargs' rezerve LogRecord alanlari oldugu icin
                # yeniden adlandirilir ( aksi halde KeyError firlatir).
                log_exception(logger, e, context={
                    'function': func.__name__,
                    'call_args': str(args)[:200],
                    'call_kwargs': str(kwargs)[:200],
                })
                raise
        return wrapper
    return decorator


# ============================================================
# FastAPI/Starlette Integration
# ============================================================

try:
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware

    class LoggingMiddleware(BaseHTTPMiddleware):
        """FastAPI middleware for request/response logging."""

        async def dispatch(self, request: Request, call_next):
            request_id = str(uuid.uuid4())[:8]
            start_time = datetime.now(timezone.utc)

            # Set request context
            set_log_context(
                request_id=request_id,
                trace_id=request.headers.get('x-trace-id', str(uuid.uuid4())[:16]),
                user_id=request.headers.get('x-user-id'),
            )

            # Log request
            logger = logging.getLogger('http.request')
            logger.info('Request started', extra={
                'method': request.method,
                'url': str(request.url),
                'client': request.client.host if request.client else None,
                'user_agent': request.headers.get('user-agent'),
            })

            try:
                response = await call_next(request)

                # Log response
                duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info('Request completed', extra={
                    'method': request.method,
                    'url': str(request.url),
                    'status_code': response.status_code,
                    'duration_ms': round(duration * 1000, 2),
                })

                response.headers['X-Request-ID'] = request_id
                return response

            except Exception as e:
                duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger = logging.getLogger('http.request')
                logger.error('Request failed', extra={
                    'method': request.method,
                    'url': str(request.url),
                    'duration_ms': round(duration * 1000, 2),
                    'error': str(e),
                })
                raise
            finally:
                clear_log_context()

except ImportError:
    # FastAPI not available
    pass


# ============================================================
# Module Exports
# ============================================================

__all__ = [
    'setup_logging',
    'get_logger',
    'mask_sensitive',
    'log_exception',
    'handle_exception',
    'LogContext',
    'set_log_context',
    'clear_log_context',
    'get_log_context',
    'JSONFormatter',
]

# LoggingMiddleware yalnizca FastAPI/Starlette kuruluysa tanimlidir.
if 'LoggingMiddleware' in globals():
    __all__.append('LoggingMiddleware')
