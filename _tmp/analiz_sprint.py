# -*- coding: utf-8 -*-
"""Gecici analiz: 4 yeni stratejik gorev + utku aktif gorev dagilimi."""
import json
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TB = "Huginn Data Insights/data/orchestrator/task_board.json"

with open(TB, "r", encoding="utf-8") as f:
    data = json.load(f)

print("TOPLAM GOREV:", len(data))
print("=" * 70)

print("\n[1] ORKESTRA- onekli 4 yeni stratejik gorev:")
for g in data:
    b = g.get("baslik", "")
    if "ORKESTRA]" in b or g.get("task_id", "").startswith("ORKESTRA-"):
        print(f"  - {g.get('task_id')} | {b}")
        print(f"      sahip={g.get('sahip')} durum={g.get('durum')} oncelik={g.get('oncelik')}")
        print(f"      brief={'VAR' if g.get('brief') else 'YOK'} talimat={'VAR' if g.get('talimat') else 'YOK'}")
        print(f"      dosyalar={g.get('dosyalar')}")

print("\n[2] Sahiplere gore AKTIF gorev dagilimi:")
sahip_aktif = {}
for g in data:
    s = g.get("sahip", "?")
    d = g.get("durum", "?")
    if d not in ("done", "archive", "tamamlandi"):
        sahip_aktif[s] = sahip_aktif.get(s, 0) + 1
for s, n in sorted(sahip_aktif.items(), key=lambda x: -x[1]):
    print(f"  {s:12s} : {n}")

print("\n[3] UTKU'nun AKTIF gorevleri (devretilecek):")
utku = [g for g in data if g.get("sahip") == "utku" and g.get("durum") not in ("done", "archive", "tamamlandi")]
for g in utku:
    print(f"  {g.get('task_id')} | {g.get('baslik', '')[:70]} | {g.get('oncelik')} | {g.get('durum')}")
print(f"  TOPLAM UTKU AKTIF: {len(utku)}")

print("\n[4] SCRAPE gorevleri:")
for g in data:
    tid = g.get("task_id", "")
    if "SCRAPE" in tid.upper():
        print(f"  {tid} | {g.get('baslik','')[:60]} | sahip={g.get('sahip')} durum={g.get('durum')}")

print("\n[5] Durum degerleri dagilimi:")
durumlar = {}
for g in data:
    durumlar[g.get("durum", "?")] = durumlar.get(g.get("durum", "?"), 0) + 1
for d, n in sorted(durumlar.items(), key=lambda x: -x[1]):
    print(f"  {d:15s} : {n}")
