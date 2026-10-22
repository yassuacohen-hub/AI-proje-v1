# -*- coding: utf-8 -*-
"""Tum ajanlarin 'done' gorevlerinde dosya/kanit varligini tarar (D-260 beyan != kanit)."""
import json, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

KOK = r"Huginn Data Insights"
P = os.path.join(KOK, "data", "orchestrator", "task_board.json")
with open(P, encoding="utf-8") as f:
    tb = json.load(f)
gorevler = tb if isinstance(tb, list) else tb.get("tasks", [])

def var_mi(d):
    for base in ("", KOK):
        if os.path.exists(os.path.join(base, d)):
            return True
    return False

# son 3 gun icinde biten (bitis alanindan) done gorevler
from datetime import datetime, timedelta
esik = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
sis = []
for t in gorevler:
    if (t.get("durum") or "").lower() != "done":
        continue
    bitis = str(t.get("bitis") or "")
    if bitis < esik:
        continue
    dosyalar = t.get("dosyalar") or []
    if isinstance(dosyalar, str):
        dosyalar = [d.strip() for d in dosyalar.replace(";", ",").split(",") if d.strip()]
    eksik = [d for d in dosyalar if not var_mi(d)]
    kanit = t.get("kanit") or ""
    if eksik or (not kanit and not dosyalar):
        sis.append((t.get("sahip"), t.get("id"), bitis[:10], eksik, kanit[:60], t.get("baslik")))

print("SON 3 GUN: done ama kanit/dosya sorunu olan gorevler:", len(sis))
for s in sis:
    print("-" * 72)
    print(f"{s[0]} | {s[1]} | bitti:{s[2]}")
    if s[3]:
        print("  EKSIK DOSYA:", s[3])
    if not s[4] and not s[3]:
        print("  KANIT ALANI BOS ve dosya listesi yok")
    print("  ", str(s[5])[:70])

ozet = {}
for s in sis:
    ozet[s[0]] = ozet.get(s[0], 0) + 1
print("\nAJAN BAZLI SUPHELI:", ozet)
