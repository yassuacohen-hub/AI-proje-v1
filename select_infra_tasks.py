#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Altyapı görevlerini seç ve utku'ya tetikle."""

import json
import sys
from pathlib import Path

# Windows cmd.exe UTF-8 çıkışı
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Board oku
board_path = Path("Huginn Data Insights/data/orchestrator/task_board.json")
with board_path.open(encoding='utf-8') as f:
    board = json.load(f)

# Altyapı görevlerini filtrele: ALTYAPI- ile başlayan, aktif/teslim, sahip!= utku
altyapi_gorevleri = []
for item in board:
    if isinstance(item, dict) and "task_id" in item:
        task_id = item.get("task_id", "")
        if task_id.startswith("ALTYAPI-"):
            durum = item.get("durum", "").lower()
            sahip = item.get("sahip", "").lower()
            oncelik = item.get("oncelik", "P2")
            
            # Aktif, teslim veya plan durumundaki görevler
            if durum in ["aktif", "teslim", "plan"] and sahip != "utku":
                altyapi_gorevleri.append({
                    "task_id": task_id,
                    "baslik": item.get("baslik", "")[:60],
                    "sahip": sahip,
                    "oncelik": oncelik,
                    "durum": durum
                })

# P0 ve P1 görevleri öncele, en az 5 tane seç
altyapi_gorevleri.sort(key=lambda x: (x["oncelik"] != "P0", x["oncelik"] != "P1", x["task_id"]))
secilen = altyapi_gorevleri[:8]

print("=== SEÇİLEN ALTYAPI GÖREVLERİ (EN AZ 5) ===\n")
for i, g in enumerate(secilen, 1):
    print(f"{i}. {g['task_id']} ({g['oncelik']}) — {g['baslik']}")
    print(f"   Sahip: {g['sahip']} → UTKU\n")

print(f"\nToplam: {len(secilen)} görev seçildi")
print("\nAdımlar:")
print("1. trigger.tetik_ekle() ile her görev utku'ya tetiklenecek")
print("2. ihsan kendi orkestratör görevlerini bitir")
print("3. Raporlar ve done işler otomatik işaretlenir")
print("4. Pano optimize edilir")
