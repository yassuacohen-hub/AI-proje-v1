# -*- coding: utf-8 -*-
"""glm-5.3 takma adi icin GUVENILIR hedef secimi: her adayi 3 kez dene,
METIN uretme oranini olc, 3/3 olanı sec (combo = tek uyeli), DB'ye yaz, dogrula.
Gerekce: 'reasoning' modelleri bazen metinsiz bitirebiliyor -> GUI'de 'bos cevap'
= kullanici icin takilmayla ayni sey. Bu yuzden hizadan once guvenirlik oncelikli."""
import json
import sqlite3
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
K = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
ADAYLAR = [
    "openrouter/nvidia/nemotron-3.5-lightning:free",
    "bzl/auto:free",
    "fullclaude",
    "openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
]
TEKRAR = 3


def deneme(model: str) -> bool:
    govde = {"model": model, "input": "Reply with exactly: OK", "stream": False}
    try:
        req = urllib.request.Request(
            "http://localhost:20128/v1/responses", data=json.dumps(govde).encode(),
            headers={"Authorization": "Bearer " + K,
                     "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=180) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
    except Exception:  # noqa: BLE001
        return False
    parca = [c.get("text") or c.get("value") or ""
             for it in (j.get("output") or []) for c in (it.get("content") or [])]
    m = " ".join(x for x in parca if x).strip()
    if not m and "choices" in j:
        m = (j["choices"][0].get("message", {}).get("content") or "").strip()
    return j.get("status") == "completed" and bool(m)


sonuclar = {}
for a in ADAYLAR:
    isabet = 0
    sn = []
    for _ in range(TEKRAR):
        t = time.time()
        if deneme(a):
            isabet += 1
        sn.append(time.time() - t)
    sonuclar[a] = (isabet, sum(sn) / len(sn))
    print(f"  {isabet}/{TEKRAR} metin  ort {sum(sn)/len(sn):5.1f}s  {a}")

kazanan = next((a for a, (i, _) in sonuclar.items() if i == TEKRAR), None)
if not kazanan:
    kazanan = max(sonuclar, key=lambda a: sonuclar[a][0])
    print("\nUYARI: 3/3 yok, en iyisi secildi:", kazanan)

con = sqlite3.connect(f"file:{DB.as_posix()}?mode=rw", uri=True)
simdi = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
con.execute("UPDATE combos SET models=?, updatedAt=? WHERE name=?",
            (json.dumps([kazanan]), simdi, "glm-5.3"))
con.commit()
print("\nglm-5.3 ->", kazanan)

iyi = sum(1 for _ in range(TEKRAR) if deneme("glm-5.3"))
print(f"DOGRULAMA takma ad: {iyi}/{TEKRAR} metin uretti")
