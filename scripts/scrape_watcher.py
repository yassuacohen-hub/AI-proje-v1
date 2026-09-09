#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Scrape watcher: OSTIM detay scrape'i izler, bitince post-scrape pipeline'ini tetikler.

Bitis tespiti (psutil'siz): firmalar_detayli.jsonl boyutu/mtime ve scraper log'unun
son yazma zamani, POLL_INTERVAL'in 2 ardisik turunda degismedigi taktirde scrape
bitti kabul edilir. Sonrasinda post_scrape_workflow.py (ingest -> VKN ->
recalculate -> KPI) calistirilir.

Kullanim:
    python scripts/scrape_watcher.py
"""
from __future__ import annotations

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "ostim" / "firmalar_detayli.jsonl"
SCRAPER_LOG = ROOT / "logs" / "ostim_detay_scrape.log"
WATCHER_LOG = ROOT / "logs" / "scrape_watcher.log"
WORKFLOW = ROOT / "scripts" / "post_scrape_workflow.py"

POLL_INTERVAL = 300  # saniye (5 dk)
STABLE_ROUNDS_NEEDED = 2


def log(msg: str) -> None:
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    with open(WATCHER_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def file_state(p: Path) -> tuple[int, float]:
    try:
        st = p.stat()
        return st.st_size, st.st_mtime
    except FileNotFoundError:
        return 0, 0.0


def scrape_finished(prev_states: list[tuple[int, float]]) -> bool:
    """2 ardisik turda veri ve log stabil ise scrape bitti kabul edilir."""
    if len(prev_states) < STABLE_ROUNDS_NEEDED + 1:
        return False
    data_states = [s[0] for s in prev_states]
    log_states = [s[1] for s in prev_states]
    data_stable = len(set(data_states[-STABLE_ROUNDS_NEEDED - 1:])) == 1
    log_stable = len(set(log_states[-STABLE_ROUNDS_NEEDED - 1:])) == 1
    return data_stable and log_stable


def main() -> int:
    log("WATCHER BASLADI — firmalar_detayli.jsonl izleniyor")
    history: list[tuple[int, float]] = []

    while True:
        d_size, d_mtime = file_state(DATA_FILE)
        _, l_mtime = file_state(SCRAPER_LOG)
        history.append((d_size, l_mtime))
        history = history[-(STABLE_ROUNDS_NEEDED + 2):]

        log(f"boyut={d_size:,} bytes | degisim kontrol: tur {len(history)}")

        if d_size > 0 and scrape_finished(history):
            log("SCRAPE BITTI tespit edildi — post-scrape workflow baslatiliyor")
            proc = subprocess.run(
                [sys.executable, str(WORKFLOW)],
                cwd=str(ROOT),
            )
            log(f"workflow tamamlandi, rc={proc.returncode}")
            if proc.returncode == 0:
                log("PIPELINE BASARILI — watcher sonlanıyor")
                return 0
            log("workflow hata verdi — 10 dk sonra tekrar denenecek")
            time.sleep(600)
            history = []  # yeniden stabilite bekleyip tekrar dene
            continue

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    sys.exit(main())