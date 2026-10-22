#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Claude hata mesajlarini derinlemesine inceleme."""
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
    "SELECT provider, model, status, timestamp, data FROM requestDetails "
    "WHERE provider='claude' AND status='error' ORDER BY timestamp DESC LIMIT 10"
)]

print("=" * 78)
print("CLAUDE HATA KAYITLARI (data field'i derinlemesine)")
print("=" * 78)
for r in rd:
    print(f"\n--- {r['model']} @ {r['timestamp']} ---")
    try:
        d = json.loads(r["data"]) if r["data"] else {}
    except Exception:
        d = {"HAM": str(r["data"])[:500]}
    # data icindeki tum anahtarlari goster
    for k, v in d.items():
        if isinstance(v, str) and len(v) > 300:
            v = v[:300] + "..."
        print(f"  {k}: {v}")
    # ozel: lastError / error / errorMessage
    for kk in ("lastError", "error", "errorMessage", "message", "errorCode", "errorType"):
        if kk in d:
            print(f"  >>> {kk}: {str(d[kk])[:250]}")

# tum hata kayitlarindaki ortak alanlari bul
print()
print("=" * 78)
print("TUM HATA KAYITLARINDAKI ANAHTARLAR")
print("=" * 78)
tum_anahtarlar = defaultdict(int)
for r in rd:
    try:
        d = json.loads(r["data"]) if r["data"] else {}
    except Exception:
        d = {}
    for k in d.keys():
        tum_anahtarlar[k] += 1
for k, c in sorted(tum_anahtarlar.items(), key=lambda x: -x[1]):
    print(f"  {k:<30} {c} kez")

# basari kayitlarindaki anahtarlar
print()
print("=" * 78)
print("TUM BASARI KAYITLARINDAKI ANAHTARLAR")
print("=" * 78)
bs = [dict(r) for r in con.execute(
    "SELECT provider, model, status, timestamp, data FROM requestDetails "
    "WHERE provider='claude' AND status='success' ORDER BY timestamp DESC LIMIT 5"
)]
tum_anahtarlar2 = defaultdict(int)
for r in bs:
    try:
        d = json.loads(r["data"]) if r["data"] else {}
    except Exception:
        d = {}
    for k in d.keys():
        tum_anahtarlar2[k] += 1
for k, c in sorted(tum_anahtarlar2.items(), key=lambda x: -x[1]):
    print(f"  {k:<30} {c} kez")

# providerConnections data'daki lastError
print()
print("=" * 78)
print("PROVIDERCONNECTIONS DATA (claude)")
print("=" * 78)
for r in con.execute("SELECT name, data FROM providerConnections WHERE provider='claude'"):
    try:
        d = json.loads(r["data"]) if r["data"] else {}
    except Exception:
        d = {}
    print(f"\n  {r['name']}:")
    for k in sorted(d.keys()):
        v = d[k]
        if isinstance(v, str) and len(v) > 200:
            v = v[:200] + "..."
        if k in ("lastError", "error", "errorMessage", "message"):
            print(f"    >>> {k}: {v}")
        else:
            print(f"    {k}: {v}")

con.close()