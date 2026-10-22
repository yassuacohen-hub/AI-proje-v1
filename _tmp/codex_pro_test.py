# -*- coding: utf-8 -*-
"""PRO sağlayıcılar Codex /responses ucundan: cx/* (ChatGPT Pro) + cc/* (Claude Pro)."""
import json
import time
import urllib.request

KEY9 = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
MODELS = [
    "cx/gpt-5.6-luna", "cx/gpt-5.6-terra", "cx/codex-auto-review",
    "cc/claude-opus-5", "cc/claude-sonnet-5", "cc/claude-fable-5",
    "fullclaude", "chatgpt-combo",
]


def test(model):
    body = {"model": model, "input": "Reply with exactly: PONG", "stream": False}
    req = urllib.request.Request(
        "http://localhost:20128/v1/responses",
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY9,
                 "Content-Type": "application/json"}, method="POST")
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
        sure = round(time.time() - t, 1)
        parc = []
        for it in j.get("output", []) or []:
            if it.get("type") == "message":
                for c in it.get("content", []) or []:
                    parc.append(c.get("text") or c.get("value") or "")
        metin = " ".join(parc).strip()
        return j.get("status", "?"), metin[:30] or json.dumps(j)[:70], sure
    except Exception as e:  # noqa: BLE001
        govde = ""
        if hasattr(e, "read"):
            try:
                govde = e.read().decode("utf-8", "replace")[:80]
            except Exception:  # noqa: BLE001
                pass
        return "HATA", (str(e)[:60] + " " + govde[:60]), round(time.time() - t, 1)


for m in MODELS:
    s, d, sn = test(m)
    print((s.ljust(10) + m.ljust(24) + f"{sn:7.1f}s ").encode(
        "ascii", "replace").decode() + d[:45].encode("ascii", "replace").decode())
