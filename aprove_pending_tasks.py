#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Tum bekleyen gorev listesi (onay_kuyrugu.json'dan)
bekleyen_task_ids = [
    "ALTYAPI-SECRETS-SETUP-01",
    "ALTYAPI-DB-MIGRATION-01",
    "TEST-BLOKE-FAKTOR-ARASTIRMA-01",
    "ALTYAPI-ADMIN-PANO-01",
    "DOC-ADMIN-DURUM-SENKRON-15",
    "API-ADMIN-AKTIVITE-YAZ-14",
    "API-ADMIN-CHURN-3SINYAL-16",
    "UI-ADMIN-ARAMA-BOSLUK-20",
    "API-ADMIN-SUPHELI-AKTIVITE-21",
    "UI-ADMIN-UPSELL-22",
    "VERI-ADMIN-AKTIVITE-LOG-13",
    "UI-ADMIN-DAU-17",
    "UI-ADMIN-GUNCELLIK-KOVA-10",
    "UI-ADMIN-MALIYET-ANOMALI-11",
    "ALTYAPI-UI-SAYFA-HIZI-02",
    "UI-ADMIN-AKTIF-KULLANICI-PROFIL-09",
    "ALTYAPI-TEMIZLIK-GER-03",
    "API-ADMIN-KAYNAK-SAGLIK-18",
]

# Task board yükle
tb_path = Path('data/orchestrator/task_board.json')
with open(tb_path, encoding='utf-8') as f:
    tasks = json.load(f)

# Güncelle
updated = 0
not_found = []

for task_id in bekleyen_task_ids:
    found = False
    for task in tasks:
        if task.get('task_id') == task_id:
            old_durum = task.get('durum', '?')
            if old_durum != 'done':
                task['durum'] = 'done'
                # bitis tarihini güncelle
                if not task.get('bitis'):
                    task['bitis'] = datetime.now().isoformat()
                updated += 1
                print("Güncellendi: {0:40} {1:10} -> done".format(task_id, old_durum))
            else:
                print("Zaten done: {0}".format(task_id))
            found = True
            break
    if not found:
        not_found.append(task_id)
        print("Bulunamadi: {0}".format(task_id))

# Kaydet
with open(tb_path, 'w', encoding='utf-8') as f:
    json.dump(tasks, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 80)
print("Toplam güncellenen: {0}".format(updated))
if not_found:
    print("Bulunamayan: {0}".format(len(not_found)))
    for tid in not_found:
        print("  - {0}".format(tid))
print("\ntask_board.json kaydedildi")
