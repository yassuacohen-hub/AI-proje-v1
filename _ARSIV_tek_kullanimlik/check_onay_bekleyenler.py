#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Teslim ettim dosyası path
teslim_path = Path('data/orchestrator/teslim_ettim.json')

if not teslim_path.exists():
    print("Teslim queue dosyası bulunamadı: {0}".format(teslim_path))
    sys.exit(0)

with open(teslim_path, encoding='utf-8') as f:
    teslimler = json.load(f)

if not teslimler:
    print("Teslim kuyruğu boş")
    sys.exit(0)

# Onay bekleyenler (status = "bekliyor")
bekleyenler = [t for t in teslimler if t.get('status', '').lower() == 'bekliyor']

if not bekleyenler:
    print("Onay bekleyen teslim yok")
    sys.exit(0)

print("\nONAY BEKLEYENLER ({0} bekleyen)".format(len(bekleyenler)))
print("=" * 120)

for i, item in enumerate(bekleyenler[:20], 1):
    task_id = item.get('task_id', '?')
    sahip = item.get('sahip', '?')
    teslim_tarihi = item.get('teslim_tarihi', '')[:10]
    not_field = item.get('not', '')[:50]
    
    print("{0:2}. {1:30} | {2:10} | {3} | {4}".format(
        i, task_id, sahip, teslim_tarihi, not_field
    ))

if len(bekleyenler) > 20:
    print("\n... ve {0} daha bekleyen teslim".format(len(bekleyenler) - 20))

print("\nToplam onay bekleyen: {0}".format(len(bekleyenler)))
