# -*- coding: utf-8 -*-
"""Gorev panosu + veri kalitesi ozet raporu."""
import json
import urllib.request
from collections import Counter

BASE = 'http://127.0.0.1:8000'

def get(path):
    return json.loads(urllib.request.urlopen(BASE + path, timeout=30).read().decode('utf-8'))

# 1) Gorev panosu
tasks = get('/api/tasks')
by_status = Counter(t['durum'] for t in tasks)
print(f"TOPLAM GOREV: {len(tasks)}")
print(f"DURUMLAR: {dict(by_status)}")
print()
print("=== ACIK GOREVLER (done haric) ===")
for t in tasks:
    if t['durum'] != 'done':
        print(f"[{t['oncelik']}] {t['task_id']}: {t['baslik']}")
        print(f"       sahip={t['sahip']} durum={t['durum']}")

# 2) Veri kalitesi
print()
print("=== VERI KALITESI ===")
try:
    kpi = get('/api/kpi')
    for k, v in kpi.items():
        print(f"  {k}: {v}")
except Exception as e:
    print(f"  KPI hatasi: {e}")

try:
    qt = get('/api/quality-trend')
    print("  Kalite dagilimi:", {x['bucket']: x['cnt'] for x in qt})
except Exception as e:
    print(f"  quality-trend hatasi: {e}")

# 3) Kaynaklar
print()
print("=== KAYNAKLAR ===")
try:
    for s in get('/api/sources'):
        print(f"  {s.get('source_name')}: {s.get('record_count')} kayit (tur={s.get('source_type')})")
except Exception as e:
    print(f"  sources hatasi: {e}")
