#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

tb_path = Path('data/orchestrator/task_board.json')
with open(tb_path, encoding='utf-8') as f:
    tasks = json.load(f)

# Acil gorevler: onem in [critical, yuksek] ve durum != done
urgent = [
    t for t in tasks 
    if t.get('onem', '').lower() in ['critical', 'yuksek'] 
    and t.get('durum', '').lower() != 'done'
]

print("\nACIL GOREVLER ({0} toplam)".format(len(urgent)))
print("=" * 90)

for i, t in enumerate(urgent[:15], 1):
    task_id = t.get('task_id', '?')
    baslik = t.get('baslik', '')[:50]
    onem = t.get('onem', '?')
    durum = t.get('durum', '?')
    sahib = t.get('sahip', '?')
    
    print("{0:2}. {1:30} | {2:50} | {3:8} | {4:8} | {5}".format(
        i, task_id, baslik, onem, durum, sahib
    ))

if len(urgent) > 15:
    print("\n... ve {0} daha acil gorev".format(len(urgent) - 15))

print("\nToplam acil: {0}".format(len(urgent)))
