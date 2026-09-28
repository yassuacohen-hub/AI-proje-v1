#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADMIN-KİT görevini pano durumunu "teslim edildi" olarak işle.
"""

import json
import sys
import io
from datetime import datetime

# UTF-8 output encoding fix for Windows cmd
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PANO_PATH = "data/orchestrator/task_board.json"

def main(task_id, ajan, ozet):
    """Görev durumunu "teslim edildi" olarak işle."""
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
    gorev["durum"] = "teslim edildi"
    gorev["bitis"] = datetime.now().isoformat()
    gorev["not"] = ozet
    pano[idx] = gorev

    try:
        with open(PANO_PATH, 'w', encoding='utf-8') as f:
            json.dump(pano, f, ensure_ascii=False, indent=2)
        print(f"OK: {task_id} durumu 'teslim edildi' olarak güncellendi")
        print(f"Bitiş: {gorev['bitis']}")
        print(f"Özet: {ozet}")
        return True
    except Exception as e:
        print(f"Hata: {PANO_PATH} yaz: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Kullanım: admin_kit_teslim.py <task_id> <ajan> <özet>")
        sys.exit(1)

    task_id = sys.argv[1]
    ajan = sys.argv[2]
    ozet = sys.argv[3]

    success = main(task_id, ajan, ozet)
    exit(0 if success else 1)
