# -*- coding: utf-8 -*-
"""Claude Pro (cc/*) ham yanıt incelemesi — içerik GERÇEKTEN geliyor mu?"""
import json
import time
import urllib.request

KEY9 = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
MODELS = ["cc/claude-opus-5", "cc/claude-sonnet-5", "cc/claude-fable-5", "fullclaude"]


def ham(model):
    body = {"model": model, "input": "Reply with exactly: PONG", "stream": False}
    req = urllib.request.Request(
        "http://localhost:20128/v1/responses", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY9,
                 "Content-Type": "application/json"}, method="POST")
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return {"model": model, "hata": str(e)[:120]}
    # her possible içerik alanını dene
    parc = []
    for it in j.get("output", []) or []:
        if isinstance(it, dict):
            for c in (it.get("content") or []):
                if isinstance(c, dict):
                    parc.append(str(c.get("text") or c.get("value") or ""))
            if it.get("type") == "output_text":
                parc.append(str(it.get("text", "")))
    metin = " ".join(parc).strip()
    # chat tarzı choices varsa onu da oku
    if not metin:
        for ch in j.get("choices", []) or []:
            metin += str(((ch or {}).get("message") or {}).get("content") or "")
    return {"model": model, "status": j.get("status"), "sure": round(time.time() - t, 1),
            "metin": metin[:60], "anahtarlar": sorted(j.keys()),
            "output_tipleri": [str((i or {}).get("type")) for i in (j.get("output") or [])][:6]}


sonuc = [ham(m) for m in MODELS]
with open("_tmp/claude_ham.json", "w", encoding="utf-8") as f:
    json.dump(sonuc, f, ensure_ascii=False, indent=1)
for s in sonuc:
    print(json.dumps(s, ensure_ascii=False)[:260].encode("ascii", "replace").decode())
