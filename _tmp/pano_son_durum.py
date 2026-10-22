#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Görev panosu son durum raporu: sahip x durum x oncelik + kritik tikanmalar."""
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

KOK = Path("Huginn Data Insights")
PANO = KOK / "data" / "orchestrator" / "task_board.json"

if not PANO.exists():
    Pano2 = Path("data/orchestrator/task_board.json")
    if Pano2.exists():
        PANO = Pano2
    else:
        print("PANO BULUNAMADI")
        sys.exit(1)

veri = json.loads(PANO.read_text(encoding="utf-8-sig"))
print(f"PANO: {PANO}")
print(f"TOPLAM KAYIT: {len(veri)}")

ACIK = {"acik", "plan", "aktif", "review", "blocked", "beklemede", "todo", "in_progress"}
KAPALI = {"tamam", "tamamlandi", "done", "kapatildi", "iptal", "arsiv"}

durum_top = Counter((t.get("durum") or "?") for t in veri)
print("\n--- DURUM DAGILIMI ---")
for d, s in durum_top.most_common():
    print(f"{d:16s} {s:5d}")

print("\n--- SAHIP x DURUM (acik isler) ---")
tablo = defaultdict(Counter)
for t in veri:
    sah = t.get("sahip") or "atanmamis"
    du = t.get("durum") or "?"
    tablo[sah][du] += 1

aciklar = defaultdict(int)
for t in veri:
    if (t.get("durum") or "") in ACIK:
        aciklar[t.get("sahip") or "atanmamis"] += 1

print(f"{'sahip':16s} {'ACIK':>5s} {'aktif':>6s} {'plan':>5s} {'review':>7s} {'blocked':>8s} {'tamam':>6s}")
for sah in sorted(tablo, key=lambda k: -aciklar.get(k, 0)):
    c = tablo[sah]
    print(f"{sah:16s} {aciklar.get(sah,0):5d} {c.get('aktif',0):6d} {c.get('plan',0):5d} "
          f"{c.get('review',0):7d} {c.get('blocked',0):8d} {c.get('tamam',0)+c.get('tamamlandi',0):6d}")

print("\n--- ONCELIK x DURUM (acik isler) ---")
onc_top = Counter((t.get("oncelik") or "-") for t in veri if (t.get("durum") or "") in ACIK)
for o, s in onc_top.most_common():
    print(f"{o:10s} {s:5d}")

print("\n--- KRITIK: ACIK + YUKSEK ONCELIK ---")
kritik = [t for t in veri if (t.get("durum") or "") in ACIK
          and (t.get("oncelik") or "").lower() in ("p0", "p1", "kritik", "yuksek", "high", "acil")]
for t in sorted(kritik, key=lambda x: str(x.get("oncelik"))):
    print(f"  {t.get('task_id','?'):28s} | {t.get('sahip','?'):10s} | {t.get('durum','?'):8s} | "
          f"{t.get('oncelik','?'):6s} | {str(t.get('baslik',''))[:52]}")

print("\n--- BLOCKED / TAKILI ---")
bl = [t for t in veri if (t.get("durum") or "") in ("blocked", "beklemede")]
for t in bl[:30]:
    dep = t.get("dependencies") or []
    print(f"  {t.get('task_id','?'):28s} | {t.get('sahip','?'):10s} | dep={dep} | {str(t.get('baslik',''))[:45]}")

print("\n--- KAPIALI OLMAYANLARIN SON GUNCELLEMESI (bayat kontrol) ---")
tarihler = []
for t in veri:
    if (t.get("durum") or "") in ACIK:
        g = t.get("guncelle") or t.get("guncellendi") or t.get("baslangic") or t.get("olusturma")
        if g:
            tarihler.append((g, t.get("task_id")))
tarihler.sort(reverse=True)
print("EN SON 10 GUNCELLENEN ACIK GOREV:")
for g, tid in tarihler[:10]:
    print(f"  {str(g)[:19]} | {tid}")
print("EN ESKI 10 ACIK GOREV (bayat riski):")
for g, tid in tarihler[-10:]:
    print(f"  {str(g)[:19]} | {tid}")

# Kahn - DAG sagligi
ids = {(t.get("task_id") or t.get("id")) for t in veri}
indeg = {i: 0 for i in ids}
edges = defaultdict(list)
for t in veri:
    nid = t.get("task_id") or t.get("id")
    for d in (t.get("dependencies") or []):
        if d in ids and d != nid:
            edges[d].append(nid)
            indeg[nid] += 1
q = [n for n, v in indeg.items() if v == 0]
seen = []
indeg2 = dict(indeg)
while q:
    n = q.pop()
    seen.append(n)
    for m in edges[n]:
        indeg2[m] -= 1
        if indeg2[m] == 0:
            q.append(m)
print(f"\n--- DAG (Kahn) ---")
print(f"dugum={len(ids)} siralanabilir={len(seen)} dongu_var_mi={len(seen)!=len(ids)}")
if len(seen) != len(ids):
    kalan = [n for n, v in indeg2.items() if v > 0]
    print(f"dongudaki dugumler: {kalan[:20]}")

# Hemen baslanabilir (acik + deps tamami kapali)
kapali_ids = {t.get("task_id") or t.get("id") for t in veri
              if (t.get("durum") or "") in KAPALI}
hazir = []
for t in veri:
    if (t.get("durum") or "") in ("acik", "plan"):
        deps = [d for d in (t.get("dependencies") or []) if d in ids]
        if all(d in kapali_ids for d in deps):
            hazir.append(t)
print(f"\n--- HEMEN BASLANABILIR (acik/plan + tum bagimliliklar kapali): {len(hazir)} ---")
for t in sorted(hazir, key=lambda x: str(x.get("oncelik"))):
    print(f"  {t.get('task_id','?'):28s} | {t.get('sahip','?'):10s} | {t.get('oncelik','?'):6s} | "
          f"{str(t.get('baslik',''))[:52]}")
