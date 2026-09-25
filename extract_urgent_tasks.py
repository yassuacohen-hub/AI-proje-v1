#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ADIM 8: Arşiv & Task Board Analizi - Acil Görevleri Çıkart"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# UTF-8 çıktı zorla
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Dosya yolları
TASK_BOARD_FILE = "Huginn Data Insights/data/orchestrator/task_board.json"
OUTPUT_DIR = "Huginn Data Insights/data/orchestrator"

# task_board.json oku
print("task_board.json okunuyor...")
with open(TASK_BOARD_FILE, 'r', encoding='utf-8') as f:
    all_tasks = json.load(f)

print(f"Toplam görev: {len(all_tasks)}")

# === FILTRELER ===

# 1. Bekleyen görevler
pending_tasks = [t for t in all_tasks if t.get('durum') == 'bekliyor']

# 2. Review görevler (acil)
review_tasks = [t for t in all_tasks if t.get('durum') == 'review']

# 3. Prefix'li görevler
admin_ux_tasks = [t for t in all_tasks if 'UI-ADMIN' in t.get('task_id', '')]
test_tasks = [t for t in all_tasks if 'TEST-' in t.get('task_id', '')]
api_tasks = [t for t in all_tasks if 'API-' in t.get('task_id', '')]

# === ÖZET ===
print("\n" + "="*60)
print("ÖZET")
print("="*60)
print(f"Bekleyen görevler: {len(pending_tasks)}")
print(f"Review görevler: {len(review_tasks)}")
print(f"UI-ADMIN görevler: {len(admin_ux_tasks)}")
print(f"TEST- görevler: {len(test_tasks)}")
print(f"API- görevler: {len(api_tasks)}")

print("\n" + "="*60)
print("BEKLEYEN GÖREVLER")
print("="*60)
for t in pending_tasks:
    print(f"\n{t.get('task_id')}")
    print(f"  Başlık: {t.get('baslik')}")
    print(f"  Sahip: {t.get('sahip')}")
    print(f"  Öncelik: {t.get('oncelik')}")
    print(f"  Not: {t.get('not', '')[:100]}...")

print("\n" + "="*60)
print("REVIEW GÖREVLER")
print("="*60)
for t in review_tasks:
    print(f"\n{t.get('task_id')}")
    print(f"  Başlık: {t.get('baslik')}")
    print(f"  Sahip: {t.get('sahip')}")
    print(f"  Öncelik: {t.get('oncelik')}")
    print(f"  Not: {t.get('not', '')[:100]}...")

# === ÖNCELİK PUANLAMA ===
def calculate_urgency_score(task):
    """Görev aciliyet puanını hesapla (1-10)"""
    score = 0
    
    # Durum
    if task.get('durum') == 'review':
        score += 8  # Review'de olan çok acil
    elif task.get('durum') == 'bekliyor':
        score += 6  # Bekleyen acil
    
    # Öncelik
    if task.get('oncelik') == 'P0':
        score += 3
    elif task.get('oncelik') == 'P1':
        score += 2
    elif task.get('oncelik') == 'P2':
        score += 1
    
    # Bağımlılık (başkasını bloke ediyorsa)
    if task.get('dependencies'):
        score += 1
    
    return min(score, 10)

# Acil görevleri bir araya topla
urgent_tasks = pending_tasks + review_tasks

# Puanlama yap
scored_tasks = []
for task in urgent_tasks:
    score = calculate_urgency_score(task)
    scored_tasks.append({
        'task_id': task.get('task_id'),
        'baslik': task.get('baslik'),
        'sahip': task.get('sahip'),
        'oncelik': task.get('oncelik'),
        'durum': task.get('durum'),
        'urgency_score': score,
        'not': task.get('not', ''),
        'dependencies': task.get('dependencies', [])
    })

# Sıra ata
scored_tasks.sort(key=lambda x: x['urgency_score'], reverse=True)

print("\n" + "="*60)
print("ÖNCELİK PUANLAMASI (SIRALANMIŞ)")
print("="*60)
for i, task in enumerate(scored_tasks, 1):
    print(f"\n{i}. {task['task_id']} - PUAN: {task['urgency_score']}/10")
    print(f"   Başlık: {task['baslik']}")
    print(f"   Durum: {task['durum']} | Öncelik: {task['oncelik']}")
    print(f"   Sahip: {task['sahip']}")

# === JSON ÇIKTILARI ===

# 1. archive_urgent_tasks.json - Arşivden acil görevler (burada yok, ama yapı var)
archive_urgent = {
    "metadata": {
        "extracted_at": datetime.now().isoformat(),
        "archive_path": "_ARSIV_geçici_2026-09-21",
        "total_found": 0
    },
    "tasks": []
}

with open(f"{OUTPUT_DIR}/archive_urgent_tasks.json", 'w', encoding='utf-8') as f:
    json.dump(archive_urgent, f, ensure_ascii=False, indent=2)
print(f"\n✓ archive_urgent_tasks.json oluşturuldu")

# 2. task_board_pending.json - Board'daki bekleyen görevler
board_pending = {
    "metadata": {
        "extracted_at": datetime.now().isoformat(),
        "total_count": len(pending_tasks)
    },
    "tasks": pending_tasks
}

with open(f"{OUTPUT_DIR}/task_board_pending.json", 'w', encoding='utf-8') as f:
    json.dump(board_pending, f, ensure_ascii=False, indent=2)
print(f"✓ task_board_pending.json oluşturuldu ({len(pending_tasks)} görev)")

# 3. urgent_tasks_ranked.json - Sıralı acil görevler
urgent_ranked = {
    "metadata": {
        "extracted_at": datetime.now().isoformat(),
        "total_urgent": len(scored_tasks),
        "breakdown": {
            "pending": len([t for t in scored_tasks if t['durum'] == 'bekliyor']),
            "review": len([t for t in scored_tasks if t['durum'] == 'review'])
        }
    },
    "tasks": scored_tasks
}

with open(f"{OUTPUT_DIR}/urgent_tasks_ranked.json", 'w', encoding='utf-8') as f:
    json.dump(urgent_ranked, f, ensure_ascii=False, indent=2)
print(f"✓ urgent_tasks_ranked.json oluşturuldu ({len(scored_tasks)} görev)")

print("\n" + "="*60)
print("ÇIKTI DOSYALARI OLUŞTURULDU")
print("="*60)
print(f"1. {OUTPUT_DIR}/archive_urgent_tasks.json")
print(f"2. {OUTPUT_DIR}/task_board_pending.json")
print(f"3. {OUTPUT_DIR}/urgent_tasks_ranked.json")
