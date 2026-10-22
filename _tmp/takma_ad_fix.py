# -*- coding: utf-8 -*-
"""3 OLU takma ad hedefini CANLI hedeflerle degistir (combos tablosu UPDATE).
Olculen: eski hedefler 503/410 donuyordu. Yeni hedefler canli testte completed."""
import json
import sqlite3
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
K = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"

DUZELTME = {
    "gpt-5.6-sol": "cx/gpt-5.6-luna",
    "deepseek-v4.1-flash": "openrouter/nvidia/nemotron-3.5-lightning:free",
    "glm-5.3": "openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
}


def pong(model: str) -> tuple[str, str]:
    govde = {"model": model, "input": "Reply with exactly: OK", "stream": False}
    try:
        req = urllib.request.Request(
            "http://localhost:20128/v1/responses", data=json.dumps(govde).encode(),
            headers={"Authorization": "Bearer " + K,
                     "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=150) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return "HATA", str(e)[:40]
    parca = [c.get("text") or c.get("value") or ""
             for it in (j.get("output") or []) for c in (it.get("content") or [])]
    m = " ".join(x for x in parca if x).strip()
    if not m and "choices" in j:
        m = (j["choices"][0].get("message", {}).get("content") or "").strip()
    return (j.get("status") or "?"), (m[:20] or "BOS")


con = sqlite3.connect(f"file:{DB.as_posix()}?mode=rw", uri=True)
con.row_factory = sqlite3.Row
simdi = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

for ad, hedef in DUZELTME.items():
    # once yeni hedefin canliligini dogrula (oluden hedefe baglama)
    st, metin = pong(hedef)
    if st != "completed":
        print(f"ATLANDI {ad}: yeni hedef de calismiyor ({hedef}) -> {st} {metin}")
        continue
    con.execute("UPDATE combos SET models=?, updatedAt=? WHERE name=?",
                (json.dumps([hedef]), simdi, ad))
    con.commit()
    print(f"GUNCELLENDI {ad:<22}-> {hedef}  (canli test: {st} {metin})")

print("\nDOGRULAMA: takma adlarin kendisi canli mi?")
for ad in DUZELTME:
    t = time.time()
    st, metin = pong(ad)
    print(f"  {st:<10}{time.time() - t:>6.1f}s {ad:<24}{metin}")
