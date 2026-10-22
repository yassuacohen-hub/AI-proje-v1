#!/usr/bin/env python3
"""9Router settings + apiKeys + providerNodes ozet."""
import json
import sqlite3
from pathlib import Path

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

row = con.execute("SELECT data FROM settings WHERE id=1").fetchone()
data = json.loads(row["data"])
print("=== settings anahtarlari ===")
for k, v in data.items():
    if isinstance(v, dict):
        print(f"  {k}: ({len(v)} alt anahtar)")
        for kk in list(v.keys())[:60]:
            print(f"      - {kk}")
    else:
        print(f"  {k} = {v!r}")

print("\n=== apiKeys ===")
for r in con.execute("SELECT * FROM apiKeys"):
    d = {k: r[k] for k in r.keys()}
    for k in list(d):
        v = str(d[k])
        if len(v) > 60 and ("key" in k.lower() or "token" in k.lower() or "secret" in k.lower()):
            d[k] = v[:12] + "...***"
    print("  ", json.dumps(d, ensure_ascii=False, default=str)[:400])

print("\n=== providerNodes ===")
cols = [c[1] for c in con.execute("PRAGMA table_info(providerNodes)")]
print("  kolonlar:", cols)
for r in con.execute("SELECT * FROM providerNodes LIMIT 60"):
    d = {k: r[k] for k in r.keys()}
    for k in list(d):
        if "key" in k.lower() or "token" in k.lower():
            d[k] = "<gizli>"
    print("  ", json.dumps(d, ensure_ascii=False, default=str)[:300])

print("\n=== combos (aktif) ===")
for r in con.execute("SELECT * FROM combos"):
    d = {k: r[k] for k in r.keys()}
    print("  ", json.dumps(d, ensure_ascii=False, default=str)[:600])
    print("  ---")

con.close()
