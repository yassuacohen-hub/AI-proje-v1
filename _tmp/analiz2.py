# -*- coding: utf-8 -*-
import json

with open('Huginn Data Insights/data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Count by status
durumlar = {}
for g in data:
    d = g.get('durum', '?')
    durumlar[d] = durumlar.get(d, 0) + 1
print('Durum dagilimi:', sorted(durumlar.items()))

# Count by sahip
sahiplar = {}
for g in data:
    s = g.get('sahip', '?')
    sahiplar[s] = sahiplar.get(s, 0) + 1
print('Sahip dagilimi:', sorted(sahiplar.items()))

# Count active (not done/archive/iptal/tamamlandi)
aktif = [g for g in data if g.get('durum') not in ('done', 'archive', 'iptal', 'tamamlandi')]
print(f'AKTIF gorev sayisi: {len(aktif)}')

# Utku'nun gorevleri
utku = [g for g in data if g.get('sahip') == 'utku']
print(f"Utku'nun toplam gorev sayisi: {len(utku)}")
for g in utku:
    print(f'  {g.get("task_id")} | {g.get("baslik", "")[:50]} | durum={g.get("durum")}')