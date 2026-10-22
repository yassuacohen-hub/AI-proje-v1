#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Derin analiz: hangi model gercekten calisiyor, hangisi oluyor."""
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

rd = [dict(r) for r in con.execute(
    "SELECT provider, model, status, timestamp, data FROM requestDetails ORDER BY timestamp DESC LIMIT 800"
)]

print("=" * 78)
print("PROVIDER x MODEL BASARI MATRISI (son 800 istek)")
print("=" * 78)

matris = defaultdict(lambda: defaultdict(lambda: {"s": 0, "e": 0}))
for r in rd:
    matris[r["provider"]][r["model"]]["s" if r["status"] == "success" else "e"] += 1

for prov in ("claude", "anthropic", "cloudflare-ai", "kilo-gateway", "cline"):
    if prov not in matris:
        continue
    print(f"\n### {prov}")
    for m in sorted(matris[prov], key=lambda x: -(matris[prov][x]["s"] + matris[prov][x]["e"])):
        d = matris[prov][m]
        t = d["s"] + d["e"]
        oran = d["s"] / t * 100 if t else 0
        bar = "#" * int(oran / 5)
        flag = "  <<< CALISIYOR" if oran >= 40 else ("  <<< HATA" if oran == 0 else "")
        print(f"  {m:<34} {d['s']:>3}/{t:<3} %{oran:>5.0f} {bar}{flag}")

# Hata mesajlarini coz
print()
print("=" * 78)
print("HATA MESAJLARI (provider bazli, cozumlu)")
print("=" * 78)
for prov in ("claude", "anthropic", "cloudflare-ai"):
    if prov not in matris:
        continue
    print(f"\n### {prov}")
    hatalar = defaultdict(int)
    for r in rd:
        if r["provider"] != prov or r["status"] != "error":
            continue
        try:
            d = json.loads(r["data"]) if r["data"] else {}
        except Exception:
            d = {}
        le = str(d.get("lastError") or d.get("error") or d.get("errorMessage") or d.get("message") or "")
        if not le:
            le = " (veri yok) " + json.dumps(d, ensure_ascii=False)[:120]
        hatalar[le[:150]] += 1
    for t, c in sorted(hatalar.items(), key=lambda x: -x[1])[:6]:
        print(f"  [{c:>3}x] {t}")

# kullanilmayan / calisan model listesi oneri
print()
print("=" * 78)
print("ONERI: CALISAN CLAUDE MODELLER (fallback icin ust sira)")
print("=" * 78)
calisan = []
for m, d in matris.get("claude", {}).items():
    t = d["s"] + d["e"]
    if t and d["s"] / t >= 0.4:
        calisan.append((d["s"] / t * 100, d["s"], t, m))
calisan.sort(reverse=True)
for oran, s, t, m in calisan:
    print(f"  {m:<34} %{oran:>5.0f}  ({s}/{t})")

print()
print("CALISMAYAN (kilitli olmali / en alta atilmali):")
for m, d in sorted(matris.get("claude", {}).items(), key=lambda x: -(matris['claude'][x]['s']+matris['claude'][x]['e'])):
    t = d["s"] + d["e"]
    if t and d["s"] / t < 0.4:
        print(f"  {m:<34} {d['s']}/{t}  (%{d['s']/t*100:.0f})")

con.close()
