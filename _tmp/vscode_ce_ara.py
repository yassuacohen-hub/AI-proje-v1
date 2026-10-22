#!/usr/bin/env python3
"""GitHub.copilot-chat state degeri + kullanici settings.json -> customOaiModels."""
import json
import sqlite3
from pathlib import Path

DB = Path.home() / "AppData/Roaming/Code/User/globalStorage/state.vscdb"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

row = con.execute("SELECT value FROM ItemTable WHERE key='GitHub.copilot-chat'").fetchone()
raw = row["value"]
try:
    data = json.loads(raw)
except Exception as e:
    print("PARSE HATA:", e)
    data = {}

print("=== GitHub.copilot-chat anahtarlari ===")
for k in data:
    v = data[k]
    s = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
    print(f"  {k} (len={len(s)})")

for key in ("github.copilot.chat.customOaiModels", "customOaiModels"):
    if key in data:
        print(f"\n=== {key} ===")
        print(json.dumps(data[key], ensure_ascii=False, indent=2)[:4000])

con.close()

print("\n\n=== KULLANICI settings.json ===")
u = Path.home() / "AppData/Roaming/Code/User/settings.json"
if u.exists():
    txt = u.read_text(encoding="utf-8", errors="ignore")
    print(txt[:6000])
else:
    print("yok")
