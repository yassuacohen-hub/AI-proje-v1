# -*- coding: utf-8 -*-
"""P7-37: Log aggregation — Loguru + PostgreSQL audit, structured logging, rotation.

Kullanim:
    from src.company_master.logging.audit_logger import AuditLogger

    logger = AuditLogger("my_module")
    logger.info("Islem tamamlandi", extra={"user_id": "u1", "action": "login"})
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import structlog

    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    structlog = None  # type: ignore

from company_master.db.connection import get_engine
from sqlalchemy import text

AUDIT_TABLE = "audit_logs"

AUDIT_LOG_SQL = """
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    level VARCHAR(10) NOT NULL,
    logger_name VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    extra JSONB DEFAULT '{}',
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    ip_address VARCHAR(45),
    action VARCHAR(100),
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    result VARCHAR(20),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_logs(resource_type, resource_id);
"""


class AuditLogger:
    """Structured audit logger with DB persistence."""

    def __init__(self, name: str = "app") -> None:
        self._name = name
        if STRUCTLOG_AVAILABLE:
            self._logger = structlog.get_logger(name)
        else:
            self._logger = logging.getLogger(name)
        self._ensure_table()

    def _ensure_table(self) -> None:
        try:
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(AUDIT_LOG_SQL))
                conn.commit()
        except Exception as e:
            logging.getLogger(__name__).warning(
                "Audit log table olusturulamadi: %s", e
            )

    def log(
        self,
        level: str,
        message: str,
        user_id: str | None = None,
        session_id: str | None = None,
        ip_address: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        result: str | None = None,
        **extra: Any,
    ) -> None:
        log_entry: dict[str, Any] = {
            "level": level,
            "logger": self._name,
            "message": message,
            "extra": extra,
        }
        if user_id:
            log_entry["user_id"] = user_id
        if session_id:
            log_entry["session_id"] = session_id
        if ip_address:
            log_entry["ip_address"] = ip_address
        if action:
            log_entry["action"] = action
        if resource_type:
            log_entry["resource_type"] = resource_type
        if resource_id:
            log_entry["resource_id"] = resource_id
        if result:
            log_entry["result"] = result

        if STRUCTLOG_AVAILABLE:
            self._logger.log(level, message, **extra)
        else:
            log_fn = getattr(self._logger, level.lower(), self._logger.info)
            log_fn(message)
        self._persist(log_entry)

    def _persist(self, entry: dict[str, Any]) -> None:
        try:
            engine = get_engine()
            columns = []
            values = []
            params: dict[str, Any] = {}
            for key, val in entry.items():
                if val is None:
                    continue
                col = key
                if isinstance(val, dict):
                    params[f"p_{col}"] = str(val)
                    values.append(f"p_{col}")
                else:
                    params[f"p_{col}"] = val
                    values.append(f"p_{col}")
                columns.append(col)

            if not columns:
                return

            col_str = ", ".join(columns)
            val_str = ", ".join(values)
            sql = f"INSERT INTO {AUDIT_TABLE} ({col_str}) VALUES ({val_str})"
            with engine.connect() as conn:
                conn.execute(text(sql), params)
                conn.commit()
        except Exception as e:
            logging.getLogger(__name__).debug("Audit persist hatasi: %s", e)

    def info(self, message: str, **extra: Any) -> None:
        self.log("INFO", message, **extra)

    def warning(self, message: str, **extra: Any) -> None:
        self.log("WARNING", message, **extra)

    def error(self, message: str, **extra: Any) -> None:
        self.log("ERROR", message, **extra)

    def critical(self, message: str, **extra: Any) -> None:
        self.log("CRITICAL", message, **extra)

    def debug(self, message: str, **extra: Any) -> None:
        self.log("DEBUG", message, **extra)

    @staticmethod
    def query_logs(
        limit: int = 100,
        user_id: str | None = None,
        action: str | None = None,
        level: str | None = None,
        days: int | None = None,
    ) -> list[dict[str, Any]]:
        """Log sorgula."""
        where: list[str] = []
        params: dict[str, Any] = {}
        if user_id:
            where.append("user_id = :user_id")
            params["user_id"] = user_id
        if action:
            where.append("action = :action")
            params["action"] = action
        if level:
            where.append("level = :level")
            params["level"] = level
        if days is not None:
            where.append("timestamp >= NOW() - :days * INTERVAL '1 day'")
            params["days"] = days

        where_sql = f" WHERE {' AND '.join(where)}" if where else ""
        sql = f"SELECT * FROM {AUDIT_TABLE}{where_sql} ORDER BY timestamp DESC LIMIT :limit"
        params["limit"] = limit

        try:
            engine = get_engine()
            with engine.connect() as conn:
                rows = conn.execute(text(sql), params).mappings().all()
                return [dict(r) for r in rows]
        except Exception:
            return []


def setup_logging(
    level: str = "INFO",
    log_file: str | None = None,
    json_format: bool = True,
) -> None:
    """Global logging ayarlari."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        stream=sys.stdout,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer() if json_format else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    ) if STRUCTLOG_AVAILABLE else logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            )
        )
        logging.getLogger().addHandler(file_handler)
