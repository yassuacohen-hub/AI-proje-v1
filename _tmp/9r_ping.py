#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""claudeAutoPing schedule'larini aktif eder + connection id eslestirmesi."""
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=rw", uri=True)
con.row_factory = sqlite3.Row

# Claude provider connection id'lerini bul
print("=" * 70)
print("CLAUDE CONNECTION ID'LERI")
print("=" * 70)
claude_ids = []
for r in con.execute("SELECT * FROM providerConnections WHERE provider='claude'"):
    cid = r["id"] if "id" in r.keys() else None
    if cid is None:
        # id kolonu yoksa tum kolonlari goster
        print(f"  (id kolonu yok) kolonlar: {list(r.keys())}")
    else:
        claude_ids.append(cid)
        print(f"  {r['name']:<12} id={cid}")

row = con.execute("SELECT data FROM settings LIMIT 1").fetchone()
st = json.loads(row["data"]) if row and row["data"] else {}

cap = st.get("claudeAutoPing") or {}
print()
print("=" * 70)
print("PING AYarlari (onceki)")
print("=" * 70)
print(json.dumps(cap, ensure_ascii=False, indent=1))

# Tum schedule'lari aktif et
cap["enabled"] = True
sched = cap.get("schedules") or {}
for k in sched:
    if isinstance(sched[k], dict):
        sched[k]["enabled"] = True
cap["schedules"] = sched

# Claude connection'larini ping listesine ekle
conns = cap.get("connections") or {}
for cid in claude_ids:
    conns[cid] = True
cap["connections"] = conns

st["claudeAutoPing"] = cap
con.execute("UPDATE settings SET data=?", (json.dumps(st, ensure_ascii=False, indent=1),))
con.commit()

print()
print("=" * 70)
print("PING AYarlari (sonraki)")
print("=" * 70)
print(json.dumps(cap, ensure_ascii=False, indent=1))

con.close()
print("\n[OK] claudeAutoPing schedule'lari aktif")
