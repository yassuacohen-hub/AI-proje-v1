#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Claude provider durumu (token yenileme sonrasi) + canli test."""
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

print("=" * 78)
print("CLAUDE PROVIDER DURUMU (token yenileme sonrasi)")
print("=" * 78)
for r in con.execute("SELECT provider,name,authType,isActive,priority,data,updatedAt FROM providerConnections WHERE provider='claude'"):
    try:
        d = json.loads(r["data"]) if r["data"] else {}
    except Exception:
        d = {}
    print(f"\n  {r['name']}  (auth={r['authType']}, aktif={r['isActive']}, prio={r['priority']})")
    print(f"    updatedAt      : {r['updatedAt']}")
    print(f"    testStatus     : {d.get('testStatus')}")
    print(f"    errorCode      : {d.get('errorCode')}")
    print(f"    backoffLevel   : {d.get('backoffLevel')}")
    print(f"    rateLimitedUntil: {d.get('rateLimitedUntil')}")
    le = d.get("lastError")
    if le:
        print(f"    lastError      : {str(le)[:220]}")
    # model lock sayisi
    locks = sum(1 for k in d.keys() if str(k).lower().startswith(("modellock", "model_lock")))
    psd = d.get("providerSpecificData") or {}
    if isinstance(psd, dict):
        locks += sum(1 for k in psd.keys() if str(k).lower().startswith(("modellock", "model_lock")))
    print(f"    modelLock sayisi: {locks}")

print()
print("=" * 78)
print("CANLI API TESTI (9Router uzerinden claude combo)")
print("=" * 78)

import urllib.request
import urllib.error
import os

KEY = os.getenv("NINEROUTER_KEY", "")
BASE = os.getenv("NINEROUTER_URL", "http://localhost:20128")
if BASE.endswith("/v1"):
    BASE = BASE[:-3]

MODELS = ["claude-claudecombo", "yasu-9router", "cc/claude-sonnet-5"]

for model in MODELS:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 10,
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {KEY}"} if KEY else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            j = json.loads(body)
            used = j.get("model", "?")
            txt = (j.get("choices") or [{}])[0].get("message", {}).get("content", "")[:60]
            print(f"  [OK  ] {model:<22} -> gercek model: {used} | cevap: {txt!r}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        print(f"  [HATA] {model:<22} -> HTTP {e.code} | {body}")
    except Exception as e:
        print(f"  [HATA] {model:<22} -> {type(e).__name__}: {e}")

con.close()
