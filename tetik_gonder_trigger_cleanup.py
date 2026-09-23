#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TRIGGER-LOGGING-CLEANUP tetiklemesi.
İhsan panoya ekledi, şimdi yasu'ya tetik gönder.
D-87 (tek komut atama) + D-68 (tetik-pano sync).
"""
import sys
import io
from pathlib import Path

# UTF-8 encoding for Windows cmd.exe
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Project root
PROJECT_ROOT = Path(__file__).parent / "Huginn Data Insights"
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from company_master.orchestrator import trigger

def main():
    task_id = "TRIGGER-LOGGING-CLEANUP"
    ajan = "yasu"
    
    print(f"[INFO] {task_id} tetiklemesi: {ajan}'ya gönderiliyor...")
    
    try:
        result = trigger.tetik_ekle(ajan, task_id)
        print(f"[OK] Tetik gönderildi: {task_id}")
        print(f"     Kuyruk dosyası: {result.get('file')}")
        print(f"     Tetik sayısı: {result.get('count')}")
        return 0
    except Exception as e:
        print(f"[ERROR] Tetik gönderme başarısız: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
