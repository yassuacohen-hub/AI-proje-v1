#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

onay_path = Path('data/orchestrator/onay_kuyrugu.json')

with open(onay_path, encoding='utf-8') as f:
    items = json.load(f)

if not items:
    print("Onay kuyrugu bos")
    sys.exit(0)

# Durum dagitimi
durumlar = Counter(item.get('durum', '?') for item in items)

print("\nONAY KUYRUGU OZETI")
print("=" * 80)
print("Toplam: {0}".format(len(items)))
print("\nDurum Dagilimi:")
for durum, count in durumlar.most_common():
    print("  {0}: {1}".format(durum, count))

# Bekleyenler
bekleyenler = [t for t in items if t.get('durum', '') not in ['onaylandi', 'reddedildi']]

if bekleyenler:
    print("\nBEKLEYEN ({0}):".format(len(bekleyenler)))
    for item in bekleyenler[:10]:
        task_id = item.get('task_id', '?')
        ajan = item.get('ajan', '?')
        durum = item.get('durum', '?')
        teslim = item.get('teslim_tarihi', '')[:10]
        print("  {0:30} | {1:10} | {2} | {3}".format(task_id, ajan, durum, teslim))
else:
    print("\nBEKLEYEN YILMADI - HEPSI ONAYLANMIS VEYA REDDEDILMIS")

# Son 5 teslim
onaylandi_list = [t for t in items if t.get('durum') == 'onaylandi']
onaylandi_sorted = sorted(onaylandi_list, key=lambda x: x.get('onay_tarihi', ''), reverse=True)

print("\nSON 5 ONAYLANAN:")
for item in onaylandi_sorted[:5]:
    task_id = item.get('task_id', '?')
    ajan = item.get('ajan', '?')
    onay_tarihi = item.get('onay_tarihi', '')[:10]
    print("  {0:30} | {1:10} | {2}".format(task_id, ajan, onay_tarihi))
