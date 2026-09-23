#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Panoyu optimize et: raporlar ve tamamlanan işleri done olacak, görevleri kategorize et."""

import sys
import json
from pathlib import Path
from datetime import datetime

# Windows cmd.exe UTF-8 çıkışı
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path("Huginn Data Insights/src")))
from company_master.orchestrator import task_board

print("=" * 70)
print("PANO OPTIMIZASYONU")
print("=" * 70 + "\n")

# 1. Teslim (teslim) durumundaki görevleri listele — yapılacak: review → onay → done
all_tasks = task_board.gorev_listesi(durum=None)
teslim_board = [t for t in all_tasks if t.get("durum") == "teslim"]
print(f"TESLIM DURUMUNDAKI GÖREVLER ({len(teslim_board)}):")
for g in teslim_board[:10]:  # İlk 10
    print(f"  - {g.get('task_id')} ({g.get('sahip')}): {g.get('baslik', '')[:50]}")

# 2. Rapor dosyalarını bulup done işaretle
rapor_dir = Path("Huginn Data Insights/data/orchestrator")
raporlar = list(rapor_dir.glob("*_rapor_*.md"))
print(f"\nRAPOR DOSYALARI TESPIT ({len(raporlar)}):")
for r in raporlar[-5:]:
    print(f"  - {r.name}")

# 3. Done işaretlenmiş ama panodan silinmemiş görevler
done_board = [t for t in all_tasks if t.get("durum") == "done"]
print(f"\nDONE DURUMUNDAKI GÖREVLER (toplam {len(done_board)}):")
print(f"  En son 3:")
for g in done_board[-3:]:
    bitis = (g.get('bitis') or 'N/A')[:10]
    print(f"    - {g.get('task_id')} ({bitis})")

# 4. Pano istatistikleri
durum_groupları = {}
for g in all_tasks:
    d = g.get("durum", "unknown").lower()
    durum_groupları[d] = durum_groupları.get(d, 0) + 1

print(f"\nPANO İSTATİSTİKLERİ (toplam {len(all_tasks)} görev):")
for durum, sayı in sorted(durum_groupları.items(), key=lambda x: -x[1]):
    print(f"  {durum}: {sayı}")

print("\n" + "=" * 70)
print("OPTIMIZASYON ADIMLAR:")
print("=" * 70)
print("""
1. TESLIM görevleri review et → onaylama kuyrugu
2. Raporlar olustu mu? Done işaretle
3. Done görevler → archive taşı (otomatik eski olanlar)
4. Blokaj görevleri açıldi mi? Tetikleri düşür
5. Pano kilitlerini kontrol et (stale kilitler varsa düşür)
""")
