#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Round Robin vs Fallback — VERIYE DAYALI analiz."""
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

row = con.execute("SELECT data FROM settings LIMIT 1").fetchone()
st = json.loads(row["data"]) if row and row["data"] else {}

print("=" * 74)
print("GUNCEL AYARLAR")
print("=" * 74)
print(f"  comboStrategy              : {st.get('comboStrategy')}")
print(f"  comboStickyRoundRobinLimit : {st.get('comboStickyRoundRobinLimit')}")
print()
print("  comboStrategies (combo bazli):")
for k, v in (st.get("comboStrategies") or {}).items():
    print(f"    {k:<20} {json.dumps(v, ensure_ascii=False)}")
print()
print("  providerStrategies (provider bazli):")
for k, v in (st.get("providerStrategies") or {}).items():
    print(f"    {k:<20} {json.dumps(v, ensure_ascii=False)}")

# ------------------------------------------------------------------ VERI
print()
print("=" * 74)
print("GECMIS VERI: CLAUDE PROVIDER BASARI ORANI")
print("=" * 74)

rd = [dict(r) for r in con.execute(
    "SELECT provider, model, status, timestamp, data FROM requestDetails ORDER BY timestamp DESC LIMIT 500"
)]

claude = [r for r in rd if r["provider"] == "claude"]
if claude:
    s = sum(1 for r in claude if r["status"] == "success")
    e = sum(1 for r in claude if r["status"] == "error")
    print(f"  claude provider: toplam={len(claude)} basari={s} hata={e} oran={s/len(claude)*100:.0f}%")
    model_durum = defaultdict(lambda: {"s": 0, "e": 0})
    for r in claude:
        model_durum[r["model"]]["s" if r["status"] == "success" else "e"] += 1
    print("  model bazli:")
    for m in sorted(model_durum, key=lambda x: -(model_durum[x]["s"] + model_durum[x]["e"])):
        d = model_durum[m]
        t = d["s"] + d["e"]
        print(f"    {m:<32} {d['s']}/{t} (%{d['s']/t*100:.0f})")
else:
    print("  claude provider icin kayit yok")

# provider geneli
print()
print("=" * 74)
print("TUM PROVIDER BASARI ORANLARI (son 500 istek)")
print("=" * 74)
ps = defaultdict(lambda: {"s": 0, "e": 0})
for r in rd:
    ps[r["provider"]]["s" if r["status"] == "success" else "e"] += 1
satirlar = []
for p, d in ps.items():
    t = d["s"] + d["e"]
    satirlar.append((p, d["s"], d["e"], t, d["s"]/t*100))
for p, s, e, t, o in sorted(satirlar, key=lambda x: -x[4]):
    bar = "#" * int(o / 5)
    print(f"  {p:<18} {s:>3}/{t:<3} %{o:>5.0f}  {bar}")

# claude hata detayi
print()
print("=" * 74)
print("CLAUDE HATA DETAYLARI (neden basarisiz?)")
print("=" * 74)
claude_err = [r for r in rd if r["provider"] == "claude" and r["status"] == "error"]
hata_tipi = defaultdict(int)
for r in claude_err:
    try:
        d = json.loads(r["data"]) if r["data"] else {}
    except Exception:
        d = {}
    le = str(d.get("lastError") or d.get("error") or d.get("message") or "")
    if "429" in le or "rate_limit" in le:
        hata_tipi["429 rate_limit"] += 1
    elif "401" in le or "unauthorized" in le.lower():
        hata_tipi["401 auth"] += 1
    else:
        hata_tipi[le[:60] or "bilinmeyen"] += 1
for t, c in sorted(hata_tipi.items(), key=lambda x: -x[1]):
    print(f"  {t:<50} {c} kez")

print()
print("=" * 74)
print("KARAR")
print("=" * 74)
print("""
Sizin icin -> FALLBACK (su anki ayar dogru, degistirme)

  Neden Round Robin DEGIL:
  - Round Robin'de her istek farkli modele gider, cc/claude-sonnet-5-5
    her zaman ustte kalmaz -> senin "en ustte olsun" istegin bozulur
  - 429 alan modele de istek atilir, her seferinde zaman kaybi
  - Claude Code tek bir model bekler; model arasi gecis yanit kalitesini
    dusurebilir (bazi modeller tool-calling / uzun baglamda daha iyi)

  Neden FALLBACK:
  + cc/claude-sonnet-5-5 her zaman once denenir
  + 429 olunca otomatik siradaki modele gecilir (Claude Code durmaz)
  + 9Router 429 alan modeli kilitler, sonraki isteklerde atlar
    (dolayisiyla "once dene" maliyeti dusuk)
""")

con.close()
