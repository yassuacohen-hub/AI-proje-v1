#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Review queue path
review_queue_path = Path('data/orchestrator/review_queue.json')

if not review_queue_path.exists():
    print("Review queue dosyası bulunamadı: {0}".format(review_queue_path))
    sys.exit(0)

with open(review_queue_path, encoding='utf-8') as f:
    queue = json.load(f)

if not queue:
    print("Review kuyruğu boş")
    sys.exit(0)

print("\nREVIEW KUYRUĞU ({0} bekleyen)".format(len(queue)))
print("=" * 100)

for i, item in enumerate(queue, 1):
    task_id = item.get('task_id', '?')
    onayla_tanimi = item.get('onayla_tanimi', '')
    onem = item.get('onem', '?')
    sahip = item.get('sahip', '?')
    ekle_tarihi = item.get('ekle_tarihi', '')[:10]
    
    print("{0:2}. {1:30} | {2} | {3} | {4} | {5}".format(
        i, task_id, onem, sahip, ekle_tarihi, onayla_tanimi[:40]
    ))

print("\nToplam bekleyen: {0}".format(len(queue)))
