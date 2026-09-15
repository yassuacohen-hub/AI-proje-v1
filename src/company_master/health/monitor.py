# -*- coding: utf-8 -*-
"""ORCH-12: Health Monitor."""

from __future__ import annotations

import json
import time
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class HealthMonitor:
    """System health checker."""

    def __init__(self):
        self.history: list[dict] = []

    def check(self) -> dict:
        checks = [
            self._check_task_board(),
            self._check_cache(),
            self._check_system(),
        ]
        healthy = sum(1 for c in checks if c["durum"] == "healthy")
        total = len(checks)
        overall = "healthy" if healthy == total else ("warning" if healthy > 0 else "degraded")
        result = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "overall": overall,
            "checks": checks,
        }
        self.history.append(result)
        return result

    def _check_task_board(self) -> dict:
        path = Path(__file__).resolve().parents[3] / "data" / "orchestrator" / "task_board.json"
        try:
            if not path.exists():
                return {"name": "task_board", "durum": "degraded", "detail": "dosya yok"}
            data = json.loads(path.read_text(encoding="utf-8"))
            n = len(data) if isinstance(data, list) else 0
            return {"name": "task_board", "durum": "healthy", "detail": f"{n} gorev", "path": str(path)}
        except Exception as exc:
            return {"name": "task_board", "durum": "degraded", "detail": str(exc)}

    def _check_cache(self) -> dict:
        try:
            import web_app
            cache = getattr(web_app, "_CACHE", None)
            if cache is None:
                return {"name": "cache", "durum": "warning", "detail": "_CACHE yok"}
            n = len(cache) if hasattr(cache, "__len__") else 0
            return {"name": "cache", "durum": "healthy", "detail": f"{n} cached", "size_kb": n}
        except Exception as exc:
            return {"name": "cache", "durum": "warning", "detail": str(exc)}

    def _check_system(self) -> dict:
        try:
            details = []
            try:
                import shutil
                usage = shutil.disk_usage("/")
                free_gb = usage.free / (1024**3)
                details.append(f"disk_free={free_gb:.1f}GB")
            except Exception:
                details.append("disk_okunamadi")
            try:
                import psutil
                mem = psutil.virtual_memory()
                details.append(f"mem_used={mem.percent}%")
            except ImportError:
                details.append("psutil_yok")
            return {"name": "system", "durum": "healthy", "detail": ", ".join(details)}
        except Exception as exc:
            return {"name": "system", "durum": "warning", "detail": str(exc)}

    def dashboard(self) -> str:
        r = self.check()
        lines = [f"=== Health: {r['overall'].upper()} ({r['ts']}) ==="]
        for c in r["checks"]:
            sim = "✅" if c["durum"] == "healthy" else ("⚠️" if c["durum"] == "warning" else "❌")
            lines.append(f"  {sim} {c['name']}: {c['durum']} \u2014 {c['detail']}")
        return "\n".join(lines)

    def endpoint(self) -> dict:
        return self.check()


if __name__ == "__main__":
    m = HealthMonitor()
    print(m.dashboard())
