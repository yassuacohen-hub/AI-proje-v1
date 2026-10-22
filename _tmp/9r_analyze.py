#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""9Router combo analizi: model saglik haritasi + strateji + oneri."""
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("Huginn Data Insights")
DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
ENV = ROOT / "data/router/model_envanter.json"

con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

# ---------------------------------------------------------------- settings
print("=" * 78)
print("SETTINGS (combo stratejisi)")
print("=" * 78)
row = con.execute("SELECT data FROM settings LIMIT 1").fetchone()
st = {}
if row and row["data"]:
    try:
        st = json.loads(row["data"])
    except Exception:
        st = {}
for k in sorted(st):
    v = st[k]
    if isinstance(v, (dict, list)):
        v = json.dumps(v, ensure_ascii=False)[:200]
    print(f"  {k} = {v}")

# ---------------------------------------------------------------- kv
print()
print("=" * 78)
print("KV (ilgili anahtarlar)")
print("=" * 78)
try:
    for r in con.execute("SELECT key, value FROM kv"):
        k = str(r["key"])
        if any(x in k.lower() for x in ("combo", "proxy", "claude", "rate", "limit", "auth")):
            print(f"  {k} = {str(r['value'])[:400]}")
except Exception as e:
    print("  kv okunamadi:", e)

# ---------------------------------------------------------------- envanter
env = json.loads(ENV.read_text(encoding="utf-8"))
OK = set(env.get("ok", []))
HATA = set(env.get("hata", []))
BOS = set(env.get("bos", []))
print()
print(f"ENVANTER: ok={len(OK)} hata={len(HATA)} bos={len(BOS)}")

# ---------------------------------------------------------------- combos
print()
print("=" * 78)
print("COMBO ANALIZI")
print("=" * 78)

combos = {}
for r in con.execute("SELECT id, name, models, updatedAt FROM combos"):
    try:
        models = json.loads(r["models"]) if r["models"] else []
    except Exception:
        models = []
    combos[r["name"]] = {"id": r["id"], "models": models, "updatedAt": r["updatedAt"]}

for name, c in combos.items():
    ms = c["models"]
    ok = [m for m in ms if m in OK]
    hata = [m for m in ms if m in HATA]
    bos = [m for m in ms if m in BOS]
    bilinmeyen = [m for m in ms if m not in OK and m not in HATA and m not in BOS]
    print(f"\n>>> {name}  (id={c['id']}, guncelleme={c['updatedAt']})")
    print(f"    toplam={len(ms):<4} calisan={len(ok):<4} hatali={len(hata):<4} bos={len(bos):<3} bilinmeyen={len(bilinmeyen)}")
    if hata:
        print(f"    HATALI ({len(hata)}): {', '.join(hata[:14])}{' ...' if len(hata) > 14 else ''}")
    if bos:
        print(f"    BOS ({len(bos)}): {', '.join(bos[:10])}")
    if bilinmeyen:
        print(f"    BILINMEYEN ({len(bilinmeyen)}): {', '.join(bilinmeyen[:10])}")

# ---------------------------------------------------------------- ucretsiz & guclu oneri
print()
print("=" * 78)
print("ONERI: ucretsiz + guclu + calisan modeller (sirali)")
print("=" * 78)

# oncelik sirasi: guclu/deneyimli ve ucretsiz olanlar one
PRIORITY = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "cohere/north-mini-code:free",
    "deepseek-ai/deepseek-r1-distill-qwen-32b",
    "qwen/qwen2.5-coder-32b-instruct",
    "qwen/qwq-32b",
    "poolside/laguna-s-2.1:free",
    "poolside/laguna-xs-2.1:free",
    "meta/llama-3.3-70b-instruct-fp8-fast",
    "meta/llama-3.1-70b-instruct-fp8-fast",
    "mistralai/mistral-small-3.1-24b-instruct",
    "z-ai/glm-4.7-flash",
]

# claude ailesi - calisanlar
claude_ok = sorted(m for m in OK if m.startswith(("cc/claude", "kr/claude", "cl/anthropic", "ag/claude", "gh/claude")))
print(f"\nClaude ailesi CALISAN modeller ({len(claude_ok)}):")
for m in claude_ok:
    print(f"  + {m}")
claude_hata = sorted(m for m in HATA if m.startswith(("cc/claude", "kr/claude", "cl/anthropic", "ag/claude", "gh/claude")))
print(f"\nClaude ailesi HATALI modeller ({len(claude_hata)}):")
for m in claude_hata:
    print(f"  - {m}")

print("\n--- ucretsiz oncelik listesi (envanterde calisan olanlar) ---")
oneri = []
for p in PRIORITY:
    hits = [m for m in OK if m.endswith(p) or p in m]
    for h in hits:
        oneri.append(h)
for m in oneri:
    print(f"  * {m}")

# claude-claudecombo icindeki hatali olmayan claude modelleri
print()
print("=" * 78)
print("claude-claudecombo -> ONERI SIRA (calisanlar one)")
print("=" * 78)
cc = combos.get("claude-claudecombo", {}).get("models", [])
temiz = [m for m in cc if m in OK]
bozuk = [m for m in cc if m in HATA or m in BOS]
print(f"calisan {len(temiz)} / bozuk {len(bozuk)}")
print("TEMIZ LISTE:")
for m in temiz:
    print(f"  {m}")

json.dump(
    {
        "combos": {k: {"id": v["id"], "models": v["models"], "updatedAt": v["updatedAt"]} for k, v in combos.items()},
        "envanter": {"ok": sorted(OK), "hata": sorted(HATA), "bos": sorted(BOS)},
        "settings": st,
    },
    open("_tmp/9r_durum.json", "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=1,
)
print("\n[OK] _tmp/9r_durum.json yazildi")
con.close()
