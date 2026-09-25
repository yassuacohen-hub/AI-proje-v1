#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test: Son mesajları kontrol et."""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.company_master.chat import oku

rows = oku()
print(f"\nToplam kayıt: {len(rows)}")
print("\nSon 5 mesaj:")
print("-" * 100)

for r in rows[-5:]:
    task_id = r.get("task_id", "N/A")
    kimden = r.get("kimden", "N/A")[:20]
    sorun = r.get("sorun", "N/A")[:40]
    durum = r.get("durum", "N/A")
    print(f"{task_id:10} | {kimden:20} | {sorun:40} | {durum}")

print("-" * 100)
