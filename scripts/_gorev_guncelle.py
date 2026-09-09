# -*- coding: utf-8 -*-
"""Gorev panosu yardimci islemleri (P4-6 gorev baslatma)."""
import sys
sys.path.insert(0, r'C:\Projeler\Huginn Data Insights\src')

from company_master.orchestrator import task_board

task_id = sys.argv[1] if len(sys.argv) > 1 else 'P4-6'
durum = sys.argv[2] if len(sys.argv) > 2 else 'aktif'
not_ = sys.argv[3] if len(sys.argv) > 3 else ''

kwargs = {}
if not_:
    kwargs['not'] = not_

result = task_board.gorev_guncelle(task_id, durum=durum, **kwargs)
if result:
    print(f"OK: {task_id} -> {durum}")
else:
    print(f"HATA: {task_id} bulunamadi")
