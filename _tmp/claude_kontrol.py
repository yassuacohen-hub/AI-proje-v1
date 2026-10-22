# -*- coding: utf-8 -*-
"""Claude Pro yenileme sonrası canlı kontrol: durum + gerçek metin + hız."""
import json
import time
import urllib.request

KEY9 = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
MODELS = ["cc/claude-opus-5", "cc/claude-sonnet-5", "cc/claude-fable-5",
          "cc/claude-opus-5-5", "cc/claude-sonnet-5-5", "fullclaude"]


def test(model):
    body = {"model": model, "input": "Reply with exactly: CLAUDE-AYAKTA",
            "stream": False}
    req = urllib.request.Request(
        "http://localhost:20128/v1/responses", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY9,
                 "Content-Type": "application/json"}, method="POST")
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        g = ""
        if hasattr(e, "read"):
            try:
                g = e.read().decode("utf-8", "replace")[:100]
            except Exception:  # noqa: BLE001
                pass
        return "HATA", str(e)[:50] + " " + g[:60], round(time.time() - t, 1)
    sure = round(time.time() - t, 1)
    parca, tipler = [], []
    for it in j.get("output", []) or []:
        tipler.append(it.get("type", "?"))
        for c in (it.get("content") or []):
            parca.append(c.get("text") or c.get("value") or "")
    metin = " ".join(parca).strip()
    durum = j.get("status") or ("METIN" if metin else "?")
    if metin:
        return durum, metin[:40], sure
    return durum, ("tipler=" + ",".join(tipler) + " | " + json.dumps(j)[:90]), sure


for m in MODELS:
    d, det, sn = test(m)
    print((str(d).ljust(11) + m.ljust(22) + f"{sn:6.1f}s ").encode(
        "ascii", "replace").decode() + det[:55].encode("ascii", "replace").decode())
