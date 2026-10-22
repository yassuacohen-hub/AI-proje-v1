# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TB = Path(r"c:\HUGINN~1\HUGINN~1\data\orchestrator\task_board.json")
data = json.loads(TB.read_text(encoding="utf-8"))

gorevler = data if isinstance(data, list) else data.get("gorevler") or data.get("tasks") or []
print(f"Toplam gorev: {len(gorevler)}")
print("=" * 70)

# yasu'ya ait tum gorevler, duruma gore
yasu = [g for g in gorevler if (g.get("sahip") or "").lower() == "yasu"]
print(f"YASU gorev sayisi: {len(yasu)}")
print("-" * 70)
durum_sayim = {}
for g in yasu:
    d = g.get("durum", "?")
    durum_sayim[d] = durum_sayim.get(d, 0) + 1
print("Durum dagilimi:", durum_sayim)
print("-" * 70)
# aktif + review olanlari ayri ayri listele
for filtre in ("aktif", "review", "in_progress", "devam"):
    eslesen = [g for g in yasu if g.get("durum") == filtre]
    if eslesen:
        print(f"\n### DURUM = {filtre} ({len(eslesen)})")
        for g in eslesen:
            print(f"  [{g.get('oncelik')}] {g.get('id')} | baslangic={g.get('baslangic')} bitis={g.get('bitis')}")
            print(f"      brief={g.get('brief')}")
