# -*- coding: utf-8 -*-
"""Son guvenilirlik turu:
 (1) qwen3.8-flash-next 152sn timeout verdi -> olculen guvenilir hedefe bagla
     (olcum: bzl/auto:free 3/3 metin, ort 4.7sn)
 (2) 14 takma adin TAMAMINI 2'şer kez dene, metin uretme oranini raporla
 Amacl: GUI listesinden secilen HICBIR model 'Dusunuyor'da takilmasin."""
import json
import sqlite3
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
K = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
ADLAR = ["gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-6-luna", "gpt-6-sol",
         "gpt-6-astra", "gpt-6.1-sol", "gpt-5.5", "gpt-daybreak-blue-latest",
         "gpt-daybreak-red-latest", "codex-auto-review", "deepseek-v4.1-flash",
         "glm-5.3", "qwen3.8-flash-next"]


def dene(model, tavan=60):
    govde = {"model": model, "input": "Reply with exactly: OK", "stream": False}
    req = urllib.request.Request(
        "http://localhost:20128/v1/responses", data=json.dumps(govde).encode(),
        headers={"Authorization": "Bearer " + K,
                 "Content-Type": "application/json"}, method="POST")
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=tavan) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return False, time.time() - t, str(e)[:28]
    sn = time.time() - t
    m = " ".join([(c.get("text") or c.get("value") or "")
                  for it in (j.get("output") or [])
                  for c in (it.get("content") or [])]).strip()
    if not m and "choices" in j:
        m = (j["choices"][0].get("message", {}).get("content") or "").strip()
    ok = (j.get("status") == "completed") and bool(m)
    return ok, sn, ("METIN" if ok else (j.get("status") or "?"))


con = sqlite3.connect(f"file:{DB.as_posix()}?mode=rw", uri=True)
simdi = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
con.execute("UPDATE combos SET models=?, updatedAt=? WHERE name=?",
            (json.dumps(["bzl/auto:free"]), simdi, "qwen3.8-flash-next"))
con.commit()
print("qwen3.8-flash-next -> bzl/auto:free (olculen 3/3, ort 4.7sn)\n")

kotu = []
for ad in ADLAR:
    sonuc = [dene(ad) for _ in range(2)]
    isabet = sum(1 for ok, _, _ in sonuc if ok)
    en_kotu = max(sn for _, sn, _ in sonuc)
    durum = "TAMAM" if isabet == 2 else "RISKLI"
    if isabet < 2:
        kotu.append(ad)
    print(f"  {durum:<7}{isabet}/2  en kotu {en_kotu:5.1f}s  {ad}")

print("\nzorluk cikaran:", kotu or "YOK — 14/14 guvenilir")
