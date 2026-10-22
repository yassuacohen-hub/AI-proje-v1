#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Claude Account 2'yi aktif eder + dogrular."""
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=rw", uri=True)
con.row_factory = sqlite3.Row

print("=" * 70)
print("ONCESI DURUM")
print("=" * 70)
for r in con.execute("SELECT name,isActive,priority FROM providerConnections WHERE provider='claude'"):
    print(f"  {r['name']:<12} | aktif={r['isActive']} | prio={r['priority']}")

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
cur = con.execute(
    "UPDATE providerConnections SET isActive=1, updatedAt=? "
    "WHERE provider='claude' AND name='Account 2'",
    (now,),
)
con.commit()
print(f"\n[UYGULANDI] {cur.rowcount} kayit guncellendi (Account 2 -> isActive=1)")

print()
print("=" * 70)
print("SONRASI DURUM")
print("=" * 70)
for r in con.execute("SELECT name,isActive,priority,data,updatedAt FROM providerConnections WHERE provider='claude'"):
    try:
        d = json.loads(r["data"]) if r["data"] else {}
    except Exception:
        d = {}
    print(f"  {r['name']:<12} | aktif={r['isActive']} | prio={r['priority']} | status={d.get('testStatus')} | err={d.get('errorCode')} | backoff={d.get('backoffLevel')}")
    print(f"                 updatedAt={r['updatedAt']}")

# claudeAutoPing connection id'lerini kontrol et
row = con.execute("SELECT data FROM settings LIMIT 1").fetchone()
st = json.loads(row["data"]) if row and row["data"] else {}
cap = st.get("claudeAutoPing") or {}
print()
print("claudeAutoPing:", json.dumps(cap, ensure_ascii=False)[:300])
print("comboStrategy :", st.get("comboStrategy"))
cs = st.get("comboStrategies") or {}
for k, v in cs.items():
    print(f"comboStrategies[{k}]:", json.dumps(v, ensure_ascii=False))

con.close()
print("\n[OK] Tamamlandi")
