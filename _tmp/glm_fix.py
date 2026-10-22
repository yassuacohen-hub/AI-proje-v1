# -*- coding: utf-8 -*-
"""glm-5.3 takma adi 'BOS' dondu (reasoning modeli metinsiz cevap uretebiliyor).
Adaylari ayri ayri olc, metin DONDUREN ilk hedefi sec, combos tablosuna yaz."""
import json
import sqlite3
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
K = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
ADAYLAR = [
    "openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "openrouter/nvidia/nemotron-3.5-lightning:free",
    "bzl/auto:free",
    "fullclaude",
]


def dene(model: str) -> tuple[str, float, str]:
    govde = {"model": model, "input": "Reply with exactly: OK", "stream": False}
    t = time.time()
    try:
        req = urllib.request.Request(
            "http://localhost:20128/v1/responses", data=json.dumps(govde).encode(),
            headers={"Authorization": "Bearer " + K,
                     "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=180) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return "HATA", time.time() - t, str(e)[:44]
    sn = time.time() - t
    parca = [c.get("text") or c.get("value") or ""
             for it in (j.get("output") or []) for c in (it.get("content") or [])]
    m = " ".join(x for x in parca if x).strip()
    if not m and "choices" in j:
        m = (j["choices"][0].get("message", {}).get("content") or "").strip()
    return (j.get("status") or "?"), sn, (m[:24] or "BOS")


secim = None
for a in ADAYLAR:
    st, sn, m = dene(a)
    print(f"  {st:<10}{sn:>6.1f}s {a:<62}{m}")
    if st == "completed" and m != "BOS":
        secim = a
        break

if not secim:
    raise SystemExit("metin donduren aday bulunamadi — combos degistirilmedi")

con = sqlite3.connect(f"file:{DB.as_posix()}?mode=rw", uri=True)
simdi = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
con.execute("UPDATE combos SET models=?, updatedAt=? WHERE name=?",
            (json.dumps([secim]), simdi, "glm-5.3"))
con.commit()
print("\nglm-5.3 yeni hedefi:", secim)
st, sn, m = dene("glm-5.3")
print(f"takma ad canli test: {st} {sn:.1f}s '{m}'")
