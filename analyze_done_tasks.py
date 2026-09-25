#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

tb_path = Path('data/orchestrator/task_board.json')
with open(tb_path, encoding='utf-8') as f:
    tasks = json.load(f)

print("\nGOREV DURUM OZETI")
print("=" * 70)
for status in ['acik', 'aktif', 'bloke', 'done', 'iptal', 'beklemede_duzeltme']:
    count = len([t for t in tasks if t.get('durum') == status])
    print("  {0:20} : {1:3}".format(status, count))

done = [t for t in tasks if t.get('durum') == 'done']
print("\n\nBITMIS ISLER ({0} toplam)".format(len(done)))
print("=" * 70)
for i, t in enumerate(done[:20], 1):
    task_id = t.get('task_id', '?')
    baslik = t.get('baslik', '')[:45]
    sahib = t.get('sahip', '?')
    print("{0:2}. {1:30} | {2:45} | {3:10}".format(i, task_id, baslik, sahib))

if len(done) > 20:
    print("\n... ve {0} daha gorev".format(len(done) - 20))

print("\nAnaliz tamamlandi.")
