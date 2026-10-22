# -*- coding: utf-8 -*-
"""Utku gorevleri durum kirilimi + modul API dogrulama."""
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TB = "Huginn Data Insights/data/orchestrator/task_board.json"
with open(TB, "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== UTKU DURUM KIRILIMI ===")
k = {}
for g in data:
    if g.get("sahip") == "utku":
        d = g.get("durum", "?")
        k[d] = k.get(d, 0) + 1
print(sorted(k.items(), key=lambda x: -x[1]))

print("\n=== UTKU 'plan' DURUMUNDAKI GOREVLER ===")
plan_utku = [g for g in data if g.get("sahip") == "utku" and g.get("durum") == "plan"]
print(f"adet: {len(plan_utku)}")
for g in plan_utku:
    print(f"  {g.get('task_id')} | {g.get('baslik','')[:55]} | P={g.get('oncelik')}")

print("\n=== TUM 'plan' GOREVLER (sahip bazinda) ===")
plan_all = [g for g in data if g.get("durum") == "plan"]
sk = {}
for g in plan_all:
    s = g.get("sahip", "?")
    sk[s] = sk.get(s, 0) + 1
print(sorted(sk.items(), key=lambda x: -x[1]))

print("\n=== YASU + SALIH AKTIF (dagilim hedefi) ===")
for sahip in ("yasu", "salih", "utku", "ihsan", "bilo", "mimir"):
    akt = [g for g in data if g.get("sahip") == sahip and g.get("durum") in ("plan", "aktif", "review")]
    print(f"  {sahip:8s} is-acik={len(akt):3d}  toplam={sum(1 for g in data if g.get('sahip')==sahip)}")

print("\n=== MODUL API DOGRULAMA ===")
sys.path.insert(0, "Huginn Data Insights")
try:
    from src.company_master.orchestrator import task_board as tb
    print("task_board import OK")
    print("  pano_oku var mi? ", hasattr(tb, "pano_oku"))
    print("  gorev_listesi var mi? ", hasattr(tb, "gorev_listesi"))
    print("  gorev_ekle var mi? ", hasattr(tb, "gorev_ekle"))
    print("  gorev_guncelle var mi? ", hasattr(tb, "gorev_guncelle"))
except Exception as e:
    print("task_board import HATA:", type(e).__name__, e)

try:
    from src.company_master.orchestrator import trigger
    print("trigger import OK")
    print("  tetik_ekle var mi? ", hasattr(trigger, "tetik_ekle"))
except Exception as e:
    print("trigger import HATA:", type(e).__name__, e)
