#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seçilen 5 altyapı görevini utku'ya ata ve tetikle."""

import sys
import json
from pathlib import Path

# Windows cmd.exe UTF-8 çıkışı
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# trigger modülünü import et
sys.path.insert(0, str(Path("Huginn Data Insights/src")))
from company_master.orchestrator import trigger

# Seçilen görevler
secilen_gorevler = [
    "ALTYAPI-D66-BYPASS-TETIKLEME",
    "ALTYAPI-D66-BYPASS-TETIKLEME-01",
    "ALTYAPI-KILIT-OTOMATIK-01",
    "ALTYAPI-MOJIBAKE-DIZIN-01",
    "ALTYAPI-TETIK-ZAMAN-01"
]

print("=" * 70)
print("ALTYAPI GOREVLERINI UTKU'YA TETIKLE")
print("=" * 70 + "\n")

tamamlandi = []
hatalar = []

for task_id in secilen_gorevler:
    try:
        sonuc = trigger.tetik_ekle(task_id, "utku")
        tamamlandi.append((task_id, sonuc))
        print(f"✓ {task_id}")
        print(f"  Tetik: {sonuc.get('created_at', 'N/A')[:19]}")
    except Exception as e:
        hatalar.append((task_id, str(e)))
        print(f"✗ {task_id}")
        print(f"  Hata: {str(e)[:80]}")
    print()

print("=" * 70)
print(f"SONUC: {len(tamamlandi)}/{len(secilen_gorevler)} tetiklendi")
if hatalar:
    print(f"HATALAR: {len(hatalar)}")
print("=" * 70)

# Kontrolü yapılan tetikleri oku
data_dir = Path("Huginn Data Insights/data/orchestrator/triggers")
utku_tetikler = data_dir / "utku.jsonl"
if utku_tetikler.exists():
    print("\nUtku tetik kuyruğu (son 5 kayıt):")
    with utku_tetikler.open(encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[-5:]:
            data = json.loads(line)
            print(f"  - {data.get('task_id', 'N/A')} ({data.get('created_at', 'N/A')[:10]})")
