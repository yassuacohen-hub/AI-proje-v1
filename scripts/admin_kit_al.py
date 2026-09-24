#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADMIN-KİT görevini pano durumunu "alındı" olarak işle.
D-65 bypass: tetik sistemi var ama elle durum güncelle.
"""

import json
import sys
import io
from datetime import datetime

# UTF-8 output encoding fix for Windows cmd
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PANO_PATH = "data/orchestrator/task_board.json"

def main():
    """Görev durumunu "alındı" olarak işle."""
    task_id = "UI-ADMIN-SAHTE-KPI-01"
    ajan = "utku"
    
    try:
        with open(PANO_PATH, 'r', encoding='utf-8') as f:
            pano = json.load(f)
    except Exception as e:
        print(f"Hata: {PANO_PATH} oku: {e}")
        return False
    
    # Görev bul
    gorev = None
    idx = -1
    for i, g in enumerate(pano):
        if g.get("task_id") == task_id:
            gorev = g
            idx = i
            break
    
    if not gorev:
        print(f"Hata: {task_id} pano'da bulunamadı")
        return False
    
    # Durum güncelle
    gorev["durum"] = "alındı"
    gorev["baslangic"] = datetime.now().isoformat()
    pano[idx] = gorev
    
    try:
        with open(PANO_PATH, 'w', encoding='utf-8') as f:
            json.dump(pano, f, ensure_ascii=False, indent=2)
        print(f"OK: {task_id} durumu 'alındı' olarak güncellendi")
        print(f"Başlangıç: {gorev['baslangic']}")
        return True
    except Exception as e:
        print(f"Hata: {PANO_PATH} yaz: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
