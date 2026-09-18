# -*- coding: utf-8 -*-
"""P7-43: Merkezi hata loglama — dosya tabanlı (DB'siz fallback).

Kullanim:
    from src.company_master.logging.error_logger import log_error, get_recent_errors

    try:
        ...
    except Exception as e:
        log_error(e, context={"user_id": "u1", "endpoint": "/api/xyz"})

    # Admin panelinde okumak icin:
    errors = get_recent_errors(limit=50)
"""
from __future__ import annotations

import json
import os
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent.parent
ERROR_LOG_DIR = ROOT / "data" / "errors"
ERROR_LOG_FILE = ERROR_LOG_DIR / "error_log.jsonl"

ERROR_LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_error(
    exc: Exception,
    context: dict[str, Any] | None = None,
    source: str = "unknown",
    level: str = "ERROR",
) -> None:
    """Hata loglar (dosyaya JSONL olarak yazar)."""
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "level": level,
        "source": source,
        "error_type": type(exc).__name__,
        "message": str(exc),
        "traceback": traceback.format_exc(),
        "context": context or {},
    }
    try:
        with ERROR_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        # Loglama hatası uygulamayı çökertmesin
        pass


def log_error_simple(
    error_type: str,
    message: str,
    traceback_str: str | None = None,
    context: dict[str, Any] | None = None,
    source: str = "unknown",
    level: str = "ERROR",
) -> None:
    """Basit hata logla (exception objesi yoksa)."""
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "level": level,
        "source": source,
        "error_type": error_type,
        "message": message,
        "traceback": traceback_str or "",
        "context": context or {},
    }
    try:
        with ERROR_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def get_recent_errors(
    limit: int = 100,
    level: str | None = None,
    source: str | None = None,
    days: int | None = None,
) -> list[dict[str, Any]]:
    """Son hatalari oku (en yeni en ustte)."""
    if not ERROR_LOG_FILE.exists():
        return []

    errors: list[dict[str, Any]] = []
    cutoff = None
    if days is not None:
        cutoff = datetime.now() - timedelta(days=days)

    with ERROR_LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if level and entry.get("level") != level:
                    continue
                if source and entry.get("source") != source:
                    continue
                if cutoff:
                    ts = datetime.fromisoformat(entry["timestamp"])
                    if ts < cutoff:
                        continue
                errors.append(entry)
            except Exception:
                continue

    # En yeni en ustte
    errors.reverse()
    return errors[:limit]


def get_error_stats(days: int = 1) -> dict[str, int]:
    """Son N gunde hata istatistikleri (turu, kaynak, level bazinda)."""
    errors = get_recent_errors(days=days)
    stats: dict[str, int] = {
        "total": len(errors),
        "by_level": {},
        "by_source": {},
        "by_type": {},
    }
    for e in errors:
        stats["by_level"][e.get("level", "UNKNOWN")] = stats["by_level"].get(e.get("level", "UNKNOWN"), 0) + 1
        stats["by_source"][e.get("source", "UNKNOWN")] = stats["by_source"].get(e.get("source", "UNKNOWN"), 0) + 1
        stats["by_type"][e.get("error_type", "UNKNOWN")] = stats["by_type"].get(e.get("error_type", "UNKNOWN"), 0) + 1
    return stats


if __name__ == "__main__":
    # Manuel test
    try:
        raise ValueError("Test hatasi")
    except Exception as e:
        log_error(e, context={"test": True}, source="manual_test")

    print("Recent errors:")
    for err in get_recent_errors(5):
        print(f"  {err['timestamp']} [{err['level']}] {err['source']}: {err['error_type']} - {err['message']}")
