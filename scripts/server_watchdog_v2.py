#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Server watchdog — FastAPI web_app.py + Streamlit app.py sürecini izler, çöküşleri loglar, Telegram bildirimi gönderir."""

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
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "server_watchdog.jsonl"

# FastAPI 8000
DEFAULT_URL = os.getenv("WATCHDOG_URL", "http://127.0.0.1:8000/api/health")
DEFAULT_INTERVAL = int(os.getenv("WATCHDOG_INTERVAL", "30"))
DEFAULT_PYTHON = os.getenv("WATCHDOG_PYTHON", str(ROOT / ".venv" / "Scripts" / "python.exe"))
DEFAULT_SCRIPT = os.getenv("WATCHDOG_SCRIPT", str(ROOT / "web_app.py"))

# Streamlit 8501
DEFAULT_URL_8501 = os.getenv("WATCHDOG_URL_8501", "http://127.0.0.1:8501/_stcore/health")
DEFAULT_PYTHON_8501 = os.getenv("WATCHDOG_PYTHON_8501", str(ROOT / ".venv" / "Scripts" / "streamlit.exe"))
DEFAULT_SCRIPT_8501 = os.getenv("WATCHDOG_SCRIPT_8501", "run app.py --logger.level=info")

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(event: dict) -> None:
    event["ts"] = now_iso()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def _telegram_gonder(message: str) -> bool:
    """Telegram bot üzerinden uyarı gönderir."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        data = urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": message}).encode()
        req = Request(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data=data,
            headers={"User-Agent": "huginn-watchdog/2.0"}
        )
        with urlopen(req, timeout=10) as resp:
            result = resp.status == 200
            if result:
                log_event({"type": "telegram_sent", "message": message[:100]})
            return result
    except Exception as e:
        log_event({"type": "telegram_error", "error": str(e)})
        return False


def check_health(url: str, timeout: int = 10) -> tuple[bool, str]:
    req = Request(url, method="GET", headers={"User-Agent": "huginn-watchdog/2.0"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            return resp.status == 200, body[:200]
    except URLError as e:
        return False, str(e.reason)
    except Exception as e:
        return False, str(e)



def start_server(python: str, script: str, port: int = 8000, shell: bool = False) -> subprocess.Popen:
    """Sunucuyu başlat."""
    log_event({"type": "restart_attempt", "python": python, "script": script, "port": port})
    out = (LOG_DIR / f"server_watchdog_{port}.stdout.log").open("a", encoding="utf-8")
    err = (LOG_DIR / f"server_watchdog_{port}.stderr.log").open("a", encoding="utf-8")
    
    if shell:
        cmd = f"{python} {script}"
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            stdout=out,
            stderr=err,
            shell=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        proc = subprocess.Popen(
            [python, script],
            cwd=str(ROOT),
            stdout=out,
            stderr=err,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    
    log_event({"type": "process_started", "pid": proc.pid, "port": port})
    return proc


def tail_summary(limit: int = 20) -> list[dict]:
    if not LOG_FILE.exists():
        return []
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-limit:] if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Huginn dual-port watchdog (8000 FastAPI + 8501 Streamlit)")
    parser.add_argument("--url", default=DEFAULT_URL, help="FastAPI health URL")
    parser.add_argument("--url-8501", default=DEFAULT_URL_8501, help="Streamlit health URL")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL)
    parser.add_argument("--python", default=DEFAULT_PYTHON)
    parser.add_argument("--script", default=DEFAULT_SCRIPT)
    parser.add_argument("--python-8501", default=DEFAULT_PYTHON_8501)
    parser.add_argument("--script-8501", default=DEFAULT_SCRIPT_8501)
    parser.add_argument("--no-restart", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    if args.status:
        print(f"Log: {LOG_FILE}")
        for ev in tail_summary():
            print(ev)
        return

    log_event({
        "type": "watchdog_started",
        "url_8000": args.url,
        "url_8501": args.url_8501,
        "interval": args.interval,
        "restart": not args.no_restart,
    })
    
    _telegram_gonder(f"🚀 Huginn Watchdog başladı (dual-port: 8000 + 8501)")

    proc_8000: subprocess.Popen | None = None
    proc_8501: subprocess.Popen | None = None
    down_since_8000: str | None = None
    down_since_8501: str | None = None

    while True:
        ok_8000, detail_8000 = check_health(args.url)
        if ok_8000:
            if down_since_8000:
                msg = f"✅ FastAPI (8000) kurtarıldı"
                log_event({"type": "recovered", "port": 8000, "detail": detail_8000})
                _telegram_gonder(msg)
                down_since_8000 = None
            log_event({"type": "healthy", "port": 8000})
        else:
            if not down_since_8000:
                down_since_8000 = now_iso()
                log_event({"type": "down_detected", "port": 8000, "detail": detail_8000})
                _telegram_gonder(f"🔴 FastAPI (8000) başarısız: {detail_8000[:80]}")
            
            if not args.no_restart:
                if proc_8000 is None or proc_8000.poll() is not None:
                    proc_8000 = start_server(args.python, args.script, port=8000)
                    _telegram_gonder(f"🔄 FastAPI yeniden başlatılıyor (PID: {proc_8000.pid})")

        ok_8501, detail_8501 = check_health(args.url_8501)
        if ok_8501:
            if down_since_8501:
                log_event({"type": "recovered", "port": 8501})
                _telegram_gonder(f"✅ Streamlit (8501) kurtarıldı")
                down_since_8501 = None
            log_event({"type": "healthy", "port": 8501})
        else:
            if not down_since_8501:
                down_since_8501 = now_iso()
                log_event({"type": "down_detected", "port": 8501, "detail": detail_8501})
                _telegram_gonder(f"🔴 Streamlit (8501) başarısız: {detail_8501[:80]}")
            
            if not args.no_restart:
                if proc_8501 is None or proc_8501.poll() is not None:
                    proc_8501 = start_server(args.python_8501, args.script_8501, port=8501, shell=True)
                    _telegram_gonder(f"🔄 Streamlit yeniden başlatılıyor (PID: {proc_8501.pid})")

        time.sleep(args.interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_event({"type": "watchdog_stopped"})
        _telegram_gonder("⏹️ Huginn Watchdog durduruldu")
        sys.exit(0)

