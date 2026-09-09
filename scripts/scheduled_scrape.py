#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Zamanlanmış scrape — daily refresh scheduler.

Kullanım:
    python scripts/scheduled_scrape.py          # sürekli döngü
    python scripts/scheduled_scrape.py --once    # tek seferlik test
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRAPER = ROOT / "src" / "company_master" / "etl" / "scrapers" / "ostim_scraper.py"
WATCHER = ROOT / "scripts" / "scrape_watcher.py"
SCHEDULE_LOG = ROOT / "logs" / "scheduled_scrape.log"


def log(msg: str) -> None:
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    with open(SCHEDULE_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_scrape() -> bool:
    """OSTIM scraper'ı çalıştır."""
    log("Scrape başlıyor...")
    try:
        result = subprocess.run(
            [sys.executable, str(SCRAPER)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=7200,
        )
        if result.returncode == 0:
            log("Scrape tamamlandı.")
            return True
        log(f"Scrape hata: {result.stderr[:200]}")
        return False
    except subprocess.TimeoutExpired:
        log("Scrape timeout (2 saat).")
        return False
    except Exception as e:
        log(f"Scrape hatası: {e}")
        return False


def run_watcher() -> None:
    """Scrape watcher'ı çalıştır."""
    log("Watcher başlıyor...")
    try:
        result = subprocess.run(
            [sys.executable, str(WATCHER)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=3600,
        )
        if result.returncode == 0:
            log("Watcher tamamlandı.")
        else:
            log(f"Watcher hata: {result.stderr[:200]}")
    except Exception as e:
        log(f"Watcher hatası: {e}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Zamanlanmış scrape")
    parser.add_argument("--once", action="store_true", help="Tek seferlik çalıştır")
    args = parser.parse_args()

    if args.once:
        run_scrape()
        run_watcher()
        return 0

    log("Zamanlanmış scrape başlıyor (günlük 02:00)...")
    while True:
        now = datetime.now()
        # Her gün 02:00'de çalıştır
        if now.hour == 2 and now.minute == 0:
            run_scrape()
            run_watcher()
            time.sleep(60)
        time.sleep(30)


if __name__ == "__main__":
    sys.exit(main())
