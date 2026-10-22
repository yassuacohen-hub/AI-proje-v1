#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""9Router DB inceleme: combos + providerConnections (claude odakli)."""
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

print("=" * 78)
print("COMBOS SCHEMA")
print("=" * 78)
for r in con.execute("PRAGMA table_info(combos)"):
    print(f"  {r['name']:<22} {r['type']}")

print()
print("=" * 78)
print("COMBOS (7 adet)")
print("=" * 78)
for r in con.execute("SELECT * FROM combos"):
    d = dict(r)
    print(f"\n--- COMBO: {d.get('name') or d.get('id')} ---")
    for k, v in d.items():
        if k in ("name", "id"):
            continue
        if isinstance(v, str) and len(v) > 2 and v.strip().startswith(("{", "[")):
            try:
                v = json.loads(v)
            except Exception:
                pass
        if isinstance(v, (dict, list)):
            print(f"  {k}: {json.dumps(v, ensure_ascii=False)[:1500]}")
        else:
            print(f"  {k}: {v}")

print()
print("=" * 78)
print("PROVIDER CONNECTIONS (37)")
print("=" * 78)
for r in con.execute(
    "SELECT provider, name, authType, isActive, priority, updatedAt, data "
    "FROM providerConnections ORDER BY provider"
):
    d = dict(r)
    data_raw = d.pop("data")
    try:
        data = json.loads(data_raw) if data_raw else {}
    except Exception:
        data = {}
    ts = data.get("testStatus")
    ec = data.get("errorCode")
    le = (data.get("lastError") or "")[:110]
    bo = data.get("backoffLevel")
    print(
        f"{d['provider']:<22} | {str(d['name'])[:26]:<26} | auth={str(d['authType'])[:10]:<10} "
        f"| aktif={d['isActive']} | prio={d['priority']} | status={ts} | err={ec} | bo={bo}"
    )
    if le:
        print(f"{'':<26} -> {le}")

con.close()
