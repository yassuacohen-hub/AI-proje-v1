# -*- coding: utf-8 -*-
"""IKI SORU, TEK TUR:
 (1) Claude Desktop'in model listesini 'customModels' (kv) mi besliyor?
     -> kv.scope='customModels' key bicimi = <providerAlias>|<tur>. 'claude' icin
        neler var? Bos ise Desktop listede neden TEK model var?
 (2) Claude Code CLI, settings.json'daki 'model' alanini DINLIYOR mu?
     -> `claude -p --output-format json` modelUsage anahtari ne diyor?
MASKELEME ZORUNLU (D-380): anahtar desenleri bastirilmaz."""
import json
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"

DESEN = re.compile(r"(nvapi-|sk-[A-Za-z0-9\-]{6,}|eyJ[A-Za-z0-9_\-]{6,}|"
                   r"ya29\.[A-Za-z0-9_\-]{6,}|ghu_[A-Za-z0-9]{6,}|"
                   r"castai_[A-Za-z0-9]{6,}|\$2b\$10\$[A-Za-z0-9./]{8,})")


def maske(s: str) -> str:
    return DESEN.sub(lambda m: m.group(1)[:8] + "…MASKELI", str(s))


con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

print("=== (1) customModels: saglayici bazinda sayim + claude kayitlari ===")
sayac = {}
claude_kayit = []
for r in con.execute("SELECT key, value FROM kv WHERE scope='customModels'"):
    alias = str(r["key"]).split("|")[0]
    sayac[alias] = sayac.get(alias, 0) + 1
    if "claude" in alias.lower() or "anthropic" in alias.lower():
        claude_kayit.append((r["key"], maske(r["value"])[:130]))
for a, n in sorted(sayac.items(), key=lambda x: -x[1]):
    print(f"  {a:<22}{n}")
print("\n  claude/anthropic aliasli kayit sayisi:", len(claude_kayit))
for k, v in claude_kayit[:10]:
    print(f"    {k}\n      {v}")

print("\n  combos tablosunda claude icerikli adlar (Desktop kutusunda gorunen):")
for r in con.execute("SELECT name FROM combos WHERE lower(name) LIKE '%claude%'"):
    print("   ", r["name"])

print("\n=== (2) Claude Code CLI settings.json 'model' alanini dinliyor mu? ===")
S = json.loads((Path.home() / ".claude" / "settings.json").read_text(encoding="utf-8"))
print("  settings.json model =", S.get("model"))
for k, v in (S.get("env") or {}).items():
    os.environ[k] = str(v)
o = subprocess.run(["claude", "-p", "Say TAMAM", "--output-format", "json"],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", timeout=240)
try:
    j = json.loads((o.stdout or "").strip())
    kullanilan = list((j.get("modelUsage") or {}).keys())
    print("  CLI'nin KULLANDIGI model:", kullanilan)
    dinliyor = any(str(S.get("model")) in str(k) for k in kullanilan)
    print("  => settings.json dinleniyor mu:",
          "EVET" if dinliyor else "HAYIR (env'deki ANTHROPIC_DEFAULT_* kazanıyor olabilir)")
    print("  env ANTHROPIC_DEFAULT_SONNET_MODEL =",
          maske((S.get("env") or {}).get("ANTHROPIC_DEFAULT_SONNET_MODEL", "?")))
except Exception as e:  # noqa: BLE001
    print("  JSON okunamadi:", str(e)[:60], (o.stdout or "")[:120])
