#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""claude-claudecombo modellerini tum combo'lara ekle, cc/claude-sonnet-5-5 en ustte."""
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=rw", uri=True)
con.row_factory = sqlite3.Row

# 1) claude-claudecombo'daki modelleri al
cc_row = con.execute("SELECT name, models FROM combos WHERE name='claude-claudecombo'").fetchone()
cc_models = json.loads(cc_row["models"]) if cc_row["models"] else []
print(f"claude-claudecombo'da {len(cc_models)} model var")

# 2) cc/claude-sonnet-5-5'i en ustte ekle (kullanici isteri)
BASLANGIC = ["cc/claude-sonnet-5-5"]
for m in cc_models:
    if m not in BASLANGIC:
        BASLANGIC.append(m)
print(f"Baslangic listesi: {len(BASLANGIC)} model (ilk: {BASLANGIC[0]})")

# 3) Tum combo'lara ekle
print()
print("=" * 70)
print("TUM COMBOLARA EKLENIYOR")
print("=" * 70)

for c in list(con.execute("SELECT id, name, models FROM combos")):
    try:
        models = json.loads(c["models"]) if c["models"] else []
    except Exception:
        models = []
    if not models:
        continue

    # cc/claude-sonnet-5-5'i basa ekle, geri kalan claude-claudecombo modellerini ekle
    mevcut = set(models)
    yeni = list(BASLANGIC)  # basa cc/claude-sonnet-5-5
    for m in cc_models:
        if m not in mevcut:
            yeni.append(m)

    # mevcut modelleri sona ekle (tekrarsiz)
    for m in models:
        if m not in yeni:
            yeni.append(m)

    if yeni != models:
        con.execute(
            "UPDATE combos SET models=?, updatedAt=? WHERE id=?",
            (json.dumps(yeni, ensure_ascii=False),
             datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
             c["id"]),
        )
        print(f"  [{c['name']:<20}] {len(models):>4} -> {len(yeni):>4} model (eklenen: {len(yeni)-len(models)})")
    else:
        print(f"  [{c['name']:<20}] degisiklik yok ({len(models)} model)")

con.commit()

# 4) Dogrula
print()
print("=" * 70)
print("DOGRLAMA")
print("=" * 70)
for c in con.execute("SELECT name, models FROM combos ORDER BY name"):
    ms = json.loads(c["models"]) if c["models"] else []
    ilk = ms[0] if ms else "-"
    print(f"  {c['name']:<20} model={len(ms):<4} ilk={ilk}")

con.close()
print("\n[OK] Tum combo'lara claude modelleri eklendi")