# -*- coding: utf-8 -*-
"""503 veren 3 takma ad icin 9Router'da CANLI hedef bul.
Yontem: aday id'leri sirayla /responses'tan kucuk PONG ile test et; ilk calisan secilir."""
import json
import time
import urllib.request

K = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
ADAYLAR = {
    "gpt-5.6-sol": ["cu/gpt-5.6-sol-medium-fast", "cu/gpt-5.6-sol-high",
                    "cu/gpt-5.6-sol-xhigh-fast", "cx/gpt-5.6-sol", "cx/gpt-5.6-luna"],
    "deepseek-v4.1-flash": ["cl/deepseek/deepseek-v4.1-flash", "kimchi/deepseek-v4.1-flash",
                            "ollama/deepseek-v4.1-flash:cloud",
                            "nvidia/deepseek-ai/deepseek-v4-pro", "fullclaude"],
    "glm-5.3": ["cl/z-ai/glm-5.3-flash", "cl/z-ai/glm-5.3",
                "tokenrouter/z-ai/glm-5.3-free", "nvidia/z-ai/glm-5.2",
                "openrouter/nvidia/nemotron-3.5-lightning:free"],
}


def pong(model):
    govde = {"model": model, "input": "Reply with exactly: OK", "stream": False}
    t = time.time()
    try:
        req = urllib.request.Request(
            "http://localhost:20128/v1/responses", data=json.dumps(govde).encode(),
            headers={"Authorization": "Bearer " + K,
                     "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=120) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return "HATA", str(e)[:34], round(time.time() - t, 1)
    parca = [c.get("text") or c.get("value") or ""
             for it in (j.get("output") or []) for c in (it.get("content") or [])]
    m = " ".join(x for x in parca if x).strip()
    if not m and "choices" in j:
        m = (j["choices"][0].get("message", {}).get("content") or "").strip()
    return (j.get("status") or "?"), (m[:20] or "BOS"), round(time.time() - t, 1)


for takma, adaylar in ADAYLAR.items():
    print("==", takma)
    for a in adaylar:
        st, metin, sn = pong(a)
        print(f"   {st:<10}{sn:>6.1f}s {a:<48}{metin}")
        if st == "completed":
            print("   >>> SECILEN HEDEF:", a)
            break
