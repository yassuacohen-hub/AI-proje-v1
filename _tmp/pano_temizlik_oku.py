#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Paket C on-inceleme: ORKESTRA-* + bayat 3 gorevin tam kaydini goster."""
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PANO = Path("Huginn Data Insights/data/orchestrator/task_board.json")
veri = json.loads(PANO.read_text(encoding="utf-8-sig"))

HEDEF = [
    "ORKESTRA-YUK-DENGELE-01",
    "ORKESTRA-WATCHDOG-OTOMATIK-01",
    "ORKESTRA-KRITIK-YOL-IZLEME-01",
    "ORKESTRA-P1-OPTIMIZASYON-01",
    "ALTYAPI-UYDU-MAKINE-01",
    "MIMIR-RAPOR-DD-01",
    "RAPOR-STANDARTI-01",
]

by_id = {t.get("task_id"): t for t in veri}
for tid in HEDEF:
    t = by_id.get(tid)
    if not t:
        print(f"[KAYIP] {tid}")
        continue
    print("=" * 78)
    print(json.dumps(t, ensure_ascii=False, indent=1))

# Kendi kanit dosyalarim var mi?
print("\n\n=== KANIT DOSYALARI (ORKESTRA isleri gercekten yapildi mi?) ===")
KOK = Path("Huginn Data Insights")
for p in [
    "scripts/gorev_devret.py",
    "scripts/makespan_watchdog.py",
    "scripts/scrape_zinciri_monitor.py",
    "data/orchestrator/watchdog_esikleri.json",
    "data/orchestrator/rapor_ozet.md",
]:
    f = KOK / p
    print(f"{'VAR ' if f.exists() else 'YOK  '} {p:52s} {f.stat().st_size if f.exists() else '-'}")
