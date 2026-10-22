#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lokal 9Router DB'sindeki kombolari cikar (SALT-OKUNUR)."""
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DB = Path.home() / "AppData" / "Roaming" / "9router" / "db" / "data.sqlite"
if not DB.exists():
    print(f"[HATA] DB yok: {DB}")
    raise SystemExit(1)

con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
rows = con.execute("SELECT id, name, kind, models FROM combos ORDER BY name").fetchall()
con.close()

sonuc = {}
for r in rows:
    try:
        modeller = json.loads(r["models"] or "[]")
    except Exception:
        modeller = []
    if not isinstance(modeller, list):
        modeller = []
    # uyeler string ya da dict olabilir -> normalize
    adlar = []
    for m in modeller:
        if isinstance(m, str):
            adlar.append(m)
        elif isinstance(m, dict):
            adlar.append(m.get("model") or m.get("id") or m.get("name") or "?")
    sonuc[r["name"]] = {"kind": r["kind"], "uyeler": adlar}

out = Path("_tmp/lokal_kombolar.json")
out.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"LOKAL kombolar: {len(sonuc)} -> {out}")
for ad, v in sorted(sonuc.items()):
    print(f"  {ad:22s} kind={v['kind']:10s} uye={len(v['uyeler'])}")
