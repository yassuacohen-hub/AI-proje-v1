# -*- coding: utf-8 -*-
"""GUI'DE 'DUSUNUYOR'DA TAKILMA — 3 ayri kanit noktasi tek bakista.
Hipotez: kullanici GUI'de bir model seciyor (ekranda deepseek-v4.1-flash gorundu),
secilen model AKTIF saglayicida (9Router) tanimli DEGIL -> Codex hic cevap
alamadan bekliyor. Ayni sekilde MCP basarisizliklari oturumu bekletebilir.
Anahtar degerleri YAZILMAZ (D-380)."""
import json
import subprocess
import tomllib
import urllib.request
from pathlib import Path

K = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
CFG = Path.home() / ".codex" / "config.toml"

with open(CFG, "rb") as f:
    d = tomllib.load(f)
prov = d.get("model_provider")
model = d.get("model")
print("[1] config.toml AKTIF:", prov, "/", model)

idler = set()
try:
    req = urllib.request.Request("http://localhost:20128/v1/models",
                                 headers={"Authorization": "Bearer " + K})
    with urllib.request.urlopen(req, timeout=40) as r:
        idler = {m.get("id") for m in json.load(r).get("data", [])}
except Exception as e:  # noqa: BLE001
    print("    9Router listesi okunamadi:", str(e)[:60])
print("    9Router'da VAR mi:", "EVET" if model in idler else "HAYIR -> TAKILMA RISKI")
if model not in idler and idler:
    parca = model.split("/")[-1].split(":")[0]
    print("    benzer 9Router id'leri:",
          ", ".join(str(i) for i in idler if parca in str(i))[:180] or "-")

print("\n[2] GUI listesi kaynaklari")
cache = Path.home() / ".codex" / "models_cache.json"
if cache.exists():
    c = json.loads(cache.read_text(encoding="utf-8"))
    gorunur = [m.get("slug") for m in c.get("models", [])
               if m.get("visibility") != "hide"]
    print("    models_cache gorunur:", len(gorunur), gorunur[:12])
    print("    icinde deepseek/GLM/qwen var mi:",
          [g for g in gorunur if any(x in str(g) for x in ("deepseek", "glm", "qwen"))])

print("\n[3] MCP durumlarini Codex'e sor")
cx = (Path.home() / "AppData/Local/OpenAI/Codex/bin/896a0166b774037a/codex.exe")
try:
    out = subprocess.run([str(cx), "mcp", "list"], capture_output=True, text=True,
                         encoding="utf-8", errors="replace", timeout=90).stdout
    satirlar = [s for s in out.splitlines() if s.strip()]
    for s in satirlar[1:]:
        parcalar = s.split()
        ad = parcalar[0] if parcalar else "?"
        durum = "enabled" if "enabled" in s else "-"
        print(f"    {ad:<22}{durum}")
except Exception as e:  # noqa: BLE001
    print("    mcp list hatasi:", str(e)[:80])

print("\n[4] Codex masaustu loglari")
for dizin in [Path.home() / "AppData/Local/OpenAI/Codex",
              Path.home() / "AppData/Roaming/OpenAI/Codex",
              Path.home() / ".codex/log"]:
    if not dizin.exists():
        continue
    loglar = sorted(dizin.rglob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    print("    ", dizin, "-> log sayisi:", len(loglar))
    for lg in loglar[:2]:
        print("      ", lg.name, lg.stat().st_size, "bayt")
