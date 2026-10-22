#!/usr/bin/env python3
"""VS Code state.vscdb icinde Roo Code provider/model ayarlarini bulur."""
import sqlite3
from pathlib import Path

DB = Path.home() / "AppData/Roaming/Code/User/globalStorage/state.vscdb"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

rows = con.execute("SELECT key, value FROM ItemTable").fetchall()
print(f"Toplam ItemTable kaydi: {len(rows)}")

interest = ("roo", "cline", "provider", "openrouter", "anthropic", "copilot",
            "model", "api", "kilo", "code")
for r in rows:
    k = r["key"]
    kl = k.lower()
    if any(t in kl for t in interest):
        v = r["value"] or ""
        print(f"\n### {k}  (uzunluk={len(v)})")
        print(v[:900])

con.close()
