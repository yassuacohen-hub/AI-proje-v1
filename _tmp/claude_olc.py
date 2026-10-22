# -*- coding: utf-8 -*-
"""CLAUDE Code / Claude Desktop model secimi icin 4 olcum (tek bakista).
1) combos tablosu: ad / tur / icindeki gercek model
2) Claude CLI var mi, surumu ne
3) Claude CLI'in okudugu ayar: ~/.claude/settings.json env + model alani
4) CANLI: ayni combo 'claude' kanalindan (Anthropic /v1/messages) cevabi mi
   -> Claude Desktop/Code Anthropic bicimini kullaniyor, Responses degil!
Anahtar degerleri yazilmaz (D-380)."""
import json
import sqlite3
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"

print("[1] COMBO'lar")
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
for r in con.execute("SELECT name, kind, models FROM combos"):
    modlar = json.loads(r["models"] or "[]")
    print(f"  {r['name']:<24}{str(r['kind']):<8}{len(modlar):>4}  {modlar[0] if modlar else '-'}")

print("\n[2] Claude CLI")
try:
    o = subprocess.run(["claude", "--version"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=60)
    print("  claude --version:", (o.stdout or o.stderr).strip()[:80] or "BOŞ")
except Exception as e:  # noqa: BLE001
    print("  CLI yok / hatasi:", str(e)[:60])

print("\n[3] Claude Code ayari (degerler maskeli)")
s = json.loads((Path.home() / ".claude" / "settings.json").read_text(encoding="utf-8"))
print("  model:", s.get("model"), "| effortLevel:", s.get("effortLevel"))
env = s.get("env", {})
for k in sorted(env):
    v = str(env[k])
    gizle = "KEY" in k or "TOKEN" in k
    print(f"  {k:<34}{'***' + v[-4:] if gizle else v[:60]}")

print("\n[4] CANLI: Anthropic bicimi (/v1/messages) combo ile")
K = "sk-9e38ba56784644a1b05592f2ccb7cd2e"   # Claude'un kullandigi cc anahtari
for model in ["claude-claudecombo", "fullclaude", "yasu-9router"]:
    govde = {"model": model, "max_tokens": 64,
             "messages": [{"role": "user", "content": "Reply with exactly: CLAUDE-OK"}]}
    req = urllib.request.Request(
        "http://127.0.0.1:20128/v1/messages", data=json.dumps(govde).encode(),
        headers={"x-api-key": K, "anthropic-version": "2023-06-01",
                 "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=150) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        print(f"  {model:<22}HATA {str(e)[:44]}")
        continue
    metin = " ".join([c.get("text", "") for c in (j.get("content") or [])]).strip()
    print(f"  {model:<22}{str(j.get('stop_reason')):<10}{metin[:30] or 'BOS'}")
