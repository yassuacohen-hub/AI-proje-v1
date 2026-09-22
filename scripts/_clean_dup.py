#!/usr/bin/env python3
"""Tetik mailbox duplikatlarını temizle."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.company_master.orchestrator import trigger

for ajan in ('ihsan', 'utku', 'salih', 'yasu'):
    kayitlar = trigger._tetikleri_oku(ajan)
    onceki = len(kayitlar)
    seen = set()
    dedupe = []
    for k in kayitlar:
        key = (k['task_id'], k['durum'])
        if key not in seen:
            seen.add(key)
            dedupe.append(k)
    if len(dedupe) < onceki:
        trigger._tetikleri_yaz(dedupe, ajan)
        print(f'{ajan}: {onceki} -> {len(dedupe)} (duplikatlar temizlendi)')
    else:
        print(f'{ajan}: temiz')
