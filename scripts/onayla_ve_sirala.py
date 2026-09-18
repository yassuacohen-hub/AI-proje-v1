#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KAHİN onayı: task_board.json'daki tüm review görevleri onayla,
açık görevleri P0>P1>P2 sırasına göre yeniden sırala ve ajan ata.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any

def main():
    board_path = Path('data/orchestrator/task_board.json')

    # Dosya oku
    with open(board_path, 'r', encoding='utf-8') as f:
        board = json.load(f)

    print("=" * 70)
    print("ADIM 1: Tüm 'review' görevleri 'done' yap (KAHİN onayı)")
    print("=" * 70)

    review_count = 0
    for task in board:
        if task.get('durum') == 'review':
            task['durum'] = 'done'
            task['bitis'] = datetime.utcnow().isoformat() + 'Z'
            review_count += 1
            print(f"[OK] {task['task_id']:25} -> done (P{task.get('oncelik', '?')})")

    print(f"\n[INFO] Toplam onaylanan: {review_count} gorev\n")

    # Açık görevleri (done olmayan) P0>P1>P2 sırasına göre yeniden sırala
    print("=" * 70)
    print("ADIM 2: Açık görevleri P0>P1>P2 sırasına göre yeniden sırala")
    print("=" * 70)

    # Açık görevleri filtrele
    open_tasks = [t for t in board if t.get('durum') != 'done']

    # Öncelik sırası (P0 > P1 > P2 > P3 > diğer)
    priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}

    open_tasks_sorted = sorted(
        open_tasks,
        key=lambda t: (
            priority_order.get(t.get('oncelik', 'P3'), 999),
            t.get('task_id', '')
        )
    )

    print("\n[LIST] Acik gorevler (yeni sira):\n")
    for idx, task in enumerate(open_tasks_sorted, 1):
        print(f"{idx:2}. {task['task_id']:25} P{task.get('oncelik','?')} {task.get('durum','-'):12} sahip={task.get('sahip','-'):15}")

    # Board'u yeni sırayla güncelle: done görevler sonda, açık görevler başta
    done_tasks = [t for t in board if t.get('durum') == 'done']
    new_board = open_tasks_sorted + done_tasks

    print(f"\n[SORT] Yeni sira: {len(open_tasks_sorted)} acik + {len(done_tasks)} done = {len(new_board)} toplam\n")

    # Dosyaya yaz
    with open(board_path, 'w', encoding='utf-8') as f:
        json.dump(new_board, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print("[OK] task_board.json basariyla guncellendi")
    print("=" * 70)

if __name__ == '__main__':
    main()
