#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADMIN-KİT pano kaydlarındaki brief yollarını düzelt.
Pano relative path kullanmalı (plans/brief_...), mutlak path değil.
"""

import json
import sys
import io

# UTF-8 output encoding fix for Windows cmd
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PANO_PATH = "data/orchestrator/task_board.json"

def main():
    """Brief yollarını düzelt."""
    try:
        with open(PANO_PATH, 'r', encoding='utf-8') as f:
            pano = json.load(f)
    except Exception as e:
        print(f"Hata: {PANO_PATH} oku: {e}")
        return False
    
    degisiklik = 0
    for gorev in pano:
        brief = gorev.get("brief", "")
        # "Huginn Data Insights/plans/brief_..." -> "plans/brief_..."
        if brief.startswith("Huginn Data Insights/plans/"):
            gorev["brief"] = brief.replace("Huginn Data Insights/", "")
            degisiklik += 1
            print(f"Düzelt: {gorev.get('task_id')} -> {gorev['brief']}")
    
    if degisiklik == 0:
        print("Düzeltme yok, tüm brief yolları OK")
        return True
    
    try:
        with open(PANO_PATH, 'w', encoding='utf-8') as f:
            json.dump(pano, f, ensure_ascii=False, indent=2)
        print(f"\nOK: {degisiklik} görev brief yolu düzeltildi")
        return True
    except Exception as e:
        print(f"Hata: {PANO_PATH} yaz: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
