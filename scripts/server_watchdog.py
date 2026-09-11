#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Server watchdog — FastAPI web_app.py sürecini izler, çöküşleri loglar ve yeniden başlatır."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "server_watchdog.jsonl"

DEFAULT_URL = os.getenv("WATCHDOG_URL", "http://127.0.0.1:8000/api/health")
DEFAULT_INTERVAL = int(os.getenv("WATCHDOG_INTERVAL", "30"))
DEFAULT_PYTHON = os.getenv("WATCHDOG_PYTHON", str(ROOT / ".venv" / "Scripts" / "python.exe"))
DEFAULT_SCRIPT = os.getenv("WATCHDOG_SCRIPT", str(ROOT / "web_app.py"))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(event: dict) -> None:
    event["ts"] = now_iso()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def check_health(url: str, timeout: int = 10) -> tuple[bool, str]:
    req = Request(url, method="GET", headers={"User-Agent": "huginn-watchdog/1.0"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            return resp.status == 200, body[:200]
    except URLError as e:
        return False, str(e.reason)
    except Exception as e:
        return False, str(e)


def start_server(python: str, script: str) -> subprocess.Popen:
    log_event({"type": "restart_attempt", "python": python, "script": script})
    out = (LOG_DIR / "server_watchdog.stdout.log").open("a", encoding="utf-8")
    err = (LOG_DIR / "server_watchdog.stderr.log").open("a", encoding="utf-8")
    proc = subprocess.Popen(
        [python, script],
        cwd=str(ROOT),
        stdout=out,
        stderr=err,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    log_event({"type": "process_started", "pid": proc.pid})
    return proc


def tail_summary(limit: int = 20) -> list[dict]:
    if not LOG_FILE.exists():
        return []
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Huginn web server watchdog")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL)
    parser.add_argument("--python", default=DEFAULT_PYTHON)
    parser.add_argument("--script", default=DEFAULT_SCRIPT)
    parser.add_argument("--no-restart", action="store_true", help="Sadece izle, yeniden başlatma")
    parser.add_argument("--status", action="store_true", help="Son log kayıtlarını göster ve çık")
    args = parser.parse_args()

    if args.status:
        print(f"Log dosyası: {LOG_FILE}")
        for ev in tail_summary():
            print(ev)
        return

    log_event({
        "type": "watchdog_started",
        "url": args.url,
        "interval": args.interval,
        "restart": not args.no_restart,
    })

    proc: subprocess.Popen | None = None
    down_since: str | None = None

    while True:
        ok, detail = check_health(args.url)
        if ok:
            if down_since:
                log_event({"type": "recovered", "down_since": down_since, "detail": detail})
                down_since = None
            log_event({"type": "healthy", "detail": detail})
        else:
            if not down_since:
                down_since = now_iso()
                log_event({"type": "down_detected", "detail": detail})
            if not args.no_restart:
                if proc is None or proc.poll() is not None:
                    proc = start_server(args.python, args.script)
                else:
                    # Süreç hâlâ çalışıyor ama sağlık kontrolü başarısız; bekle ve tekrar dene.
                    log_event({"type": "unhealthy_process_alive", "pid": proc.pid, "detail": detail})

        time.sleep(args.interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_event({"type": "watchdog_stopped", "reason": "keyboard_interrupt"})
        sys.exit(0)
