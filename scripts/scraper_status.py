#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Scraper durumunu kontrol et."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "data/ostim/.scrape_state.json"
LOG_PATH = ROOT / "logs/ostim_detay_scrape.log"


def main() -> int:
    if STATE_PATH.exists():
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)
        completed = state.get("completed_sectors", {})
        total_records = state.get("total_records", 0)
        print(f"Tamamlanan sektorler: {len(completed)}")
        for slug, page in completed.items():
            print(f"  {slug}: sayfa {page}")
        print(f"Toplam kayit: {total_records}")
    else:
        print("State dosyasi bulunamadi. Scraper henuz baslamadi veya state kaybi olusmus.")

    if LOG_PATH.exists():
        lines = LOG_PATH.read_text(encoding="utf-8").splitlines()
        print(f"\nLog satirlari: {len(lines)}")
        if lines:
            print(f"Son log: {lines[-1]}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
