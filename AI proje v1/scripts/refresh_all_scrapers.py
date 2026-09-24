#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tüm scraper'ları sırayla çalıştıran zamanlanmış görev.

Kullanım:
    python scripts/refresh_all_scrapers.py          # tüm scraper'lar
    python scripts/refresh_all_scrapers.py --once    # tek seferlik (systemd/timer ile aynı)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.utils.telegram_bot import send_message

LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "refresh_all_scrapers.log"

SCRAPERS = [
    {
        "name": "OSTIM detay",
        "cmd": [sys.executable, "-m", "company_master.etl.scrapers.ostim_scraper", "--detayli", "data/ostim/firmalar_detayli.jsonl"],
        "timeout": 7200,
    },
    {
        "name": "İvedik OSB",
        "cmd": [sys.executable, "-m", "company_master.etl.scrapers.ivedik_scraper", "--detayli", "data/ivedik/firmalar.jsonl"],
        "timeout": 7200,
    },
    {
        "name": "Başkent OSB",
        "cmd": [sys.executable, "-m", "company_master.etl.scrapers.baskent_scraper", "--detayli", "data/baskent/firmalar.jsonl"],
        "timeout": 7200,
    },
    {
        "name": "ASO",
        "cmd": [sys.executable, "-c", "from company_master.etl.scrapers.aso_scraper import run_full_scrape; run_full_scrape()"],
        "timeout": 7200,
    },
]


def log(msg: str) -> None:
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_scraper(scraper: dict) -> bool:
    name = scraper["name"]
    cmd = scraper["cmd"]
    timeout = scraper["timeout"]
    log(f"Başlıyor: {name} -> {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            log(f"Tamamlandı: {name}")
            if result.stdout.strip():
                log(f"  stdout: {result.stdout.strip()[:500]}")
            return True
        log(f"HATA {name}: rc={result.returncode} stderr={result.stderr[:500]}")
        return False
    except subprocess.TimeoutExpired:
        log(f"HATA {name}: timeout ({timeout}s)")
        return False
    except Exception as exc:
        log(f"HATA {name}: {exc}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Tüm scraper'ları sırayla çalıştır")
    parser.add_argument("--once", action="store_true", help="Tek seferlik çalıştır (varsayılan)")
    args = parser.parse_args()

    log("=" * 60)
    log("refresh_all_scrapers BAŞLIYOR")
    results = {}
    for scraper in SCRAPERS:
        ok = run_scraper(scraper)
        results[scraper["name"]] = "OK" if ok else "HATA"
        time.sleep(5)

    log("SONUÇLAR:")
    for name, status in results.items():
        log(f"  {name}: {status}")

    failed = [n for n, s in results.items() if s != "OK"]
    if failed:
        send_message(
            f"⚠️ <b>Scrape Hatası</b>\nHatalı scraper'lar:\n" + "\n".join(f"- {n}" for n in failed)
        )
        return 1

    send_message(
        f"✅ <b>Tüm Scraper'lar Tamamlandı</b>\n"
        + "\n".join(f"- {n}: {s}" for n, s in results.items())
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
