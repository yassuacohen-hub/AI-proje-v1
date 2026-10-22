#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""9Router combo duzenleme: hatali modelleri temizle, calisanlari koru, guclu ucretsizleri one cikar."""
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("Huginn Data Insights")
ENV = ROOT / "data/router/model_envanter.json"
DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"

env = json.loads(ENV.read_text(encoding="utf-8"))
OK = set(env.get("ok", []))
HATA = set(env.get("hata", []))
BOS = set(env.get("bos", []))

# Oncelik sirasi: guclu + ucretsiz + calisan
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

def sirala(models):
    """Oncelik sirasina gore sirala, calisanlar once, bozuklar sona."""
    calisan = [m for m in models if m in OK]
    bozuk = [m for m in models if m not in OK]
    # calisanlari oncelik sirasina gore
    def oncelik(m):
        for i, p in enumerate(PRIORITY):
            if m.endswith(p) or p in m:
                return i
        return 999
    calisan.sort(key=oncelik)
    return calisan + bozuk

con = sqlite3.connect(f"file:{DB.as_posix()}?mode=rw", uri=True)
con.row_factory = sqlite3.Row

combos = list(con.execute("SELECT id, name, models FROM combos"))
print(f"Toplam combo: {len(combos)}")

for c in combos:
    try:
        models = json.loads(c["models"]) if c["models"] else []
    except Exception:
        models = []
    if not models:
        continue
    onceki = len(models)
    yeni = sirala(models)
    # tekrarsiz yap
    seen = set()
    yeni_tekrarsiz = []
    for m in yeni:
        if m not in seen:
            yeni_tekrarsiz.append(m)
            seen.add(m)
    yeni = yeni_tekrarsiz
    if yeni != models:
        con.execute(
            "UPDATE combos SET models=? WHERE id=?",
            (json.dumps(yeni, ensure_ascii=False), c["id"]),
        )
        print(f"[{c['name']}] {onceki} -> {len(yeni)} model (duzenlendi)")
    else:
        print(f"[{c['name']}] degisiklik yok ({onceki} model)")

con.commit()
con.close()
print("\n[OK] Combo'lar duzenlendi ve DB'ye yazildi.")
