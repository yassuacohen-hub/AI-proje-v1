#!/usr/bin/env python3
"""VS Code Chat / Copilot BYOK custom OAI model ayarlarini bulur."""
import json
import sqlite3
from pathlib import Path

DB = Path.home() / "AppData/Roaming/Code/User/globalStorage/state.vscdb"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

print("=== 'custom' / 'byok' / 'oai' iceren state anahtarlari ===")
for r in con.execute("SELECT key, value FROM ItemTable"):
    k = r["key"]
    kl = k.lower()
    if any(t in kl for t in ("customoai", "byok", "customendpoint", "oai", "endpoint")):
        v = r["value"] or ""
        print(f"\n### {k} (len={len(v)})")
        print(v[:2000])

print("\n\n=== chat.cachedLanguageModels.v2 icindeki customendpoint kayitlari ===")
row = con.execute(
    "SELECT value FROM ItemTable WHERE key='chat.cachedLanguageModels.v2'"
).fetchone()
if row:
    models = json.loads(row["value"])
    for m in models:
        ident = m.get("identifier", "")
        if "custom" in ident.lower() or "9router" in ident.lower():
            print(json.dumps(m, ensure_ascii=False, indent=2)[:1200])
            print("---")

print("\n\n=== state.vscdb icindeki 'github.copilot.chat' anahtarlari ===")
for r in con.execute("SELECT key, value FROM ItemTable WHERE key LIKE 'github.copilot%'"):
    print(f"- {r['key']} (len={len(r['value'] or '')})")

con.close()
