#!/usr/bin/env python3
"""9Router DB icinde VS Code / code tool / cline ile ilgili ayar ve model arar."""
import json
import sqlite3
from pathlib import Path

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"

con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

print("=== TABLOLAR ===")
for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(" -", r["name"])

print("\n=== settings TABLASI ===")
try:
    for r in con.execute("SELECT * FROM settings"):
        for k in r.keys():
            v = r[k]
            if isinstance(v, str) and len(v) > 400:
                v = v[:400] + "... [KIRPILDI]"
            print(f"  {k} = {v}")
except Exception as e:
    print("  HATA:", e)

print("\n=== kv TABLASI (anahtar filtre) ===")
try:
    for r in con.execute("SELECT * FROM kv"):
        s = json.dumps({k: r[k] for k in r.keys()}, ensure_ascii=False, default=str)
        low = s.lower()
        if any(t in low for t in ("vscode", "vs code", "cline", "code tool", "codetool", "copilot", "cursor", "mcp", "anthropic", "endpoint", "baseurl", "base_url", "api_key", "apikey")):
            print("  ", s[:1200])
            print("  ---")
except Exception as e:
    print("  HATA:", e)

con.close()
