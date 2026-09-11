#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""server_watchdog.jsonl logundan basit uptime/downtime raporu üretir."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT / "logs" / "server_watchdog.jsonl"


def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def main() -> None:
    if not LOG_FILE.exists():
        print("Henüz log yok.")
        sys.exit(0)

    events = [json.loads(line) for line in LOG_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]

    if not events:
        print("Log dosyası boş.")
        return

    down_events = [e for e in events if e.get("type") == "down_detected"]
    recovered_events = [e for e in events if e.get("type") == "recovered"]
    restarts = [e for e in events if e.get("type") == "restart_attempt"]

    print(f"Toplam kayıt: {len(events)}")
    print(f"Tespit edilen kopma: {len(down_events)}")
    print(f"Yeniden başlatma: {len(restarts)}")
    print(f"İyileşme: {len(recovered_events)}")

    if down_events:
        print("\nSon kopmalar:")
        for down in down_events[-10:]:
            start = parse_ts(down["ts"])
            detail = down.get("detail", "")
            print(f"  - {start:%Y-%m-%d %H:%M:%S}  {detail[:60]}")

    if events:
        first = parse_ts(events[0]["ts"])
        last = parse_ts(events[-1]["ts"])
        total_sec = (last - first).total_seconds()
        # Basit uptime: healthy kayitlarinin toplami * interval
        healthy_count = sum(1 for e in events if e.get("type") == "healthy")
        interval = events[0].get("interval", 30)
        monitored_sec = healthy_count * interval
        if total_sec > 0:
            uptime_pct = min(100.0, monitored_sec / total_sec * 100)
            print(f"\nİzlenen süre: ~{total_sec/60:.1f} dk")
            print(f"Tahmini uptime: %{uptime_pct:.1f}")


if __name__ == "__main__":
    main()
