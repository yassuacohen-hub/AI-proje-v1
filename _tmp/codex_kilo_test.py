# -*- coding: utf-8 -*-
"""Kilo (kr/) modelleri 9Router üzerinden canlı test — profil listesine girmeden önce ölçüm."""
import json
import urllib.request

BASE = "http://localhost:20128/v1/chat/completions"
KEY = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
MODELS = [
    "kr/claude-haiku-4.5", "kr/claude-sonnet-4.5", "kr/claude-sonnet-4",
    "kr/qwen3-coder-next", "kr/deepseek-3.2", "kr/glm-5",
    "kr/minimax-m2.5", "kr/auto",
    "bzl/auto:free", "cl/minimax/minimax-m3.1-flash:free",
    "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
    "kc/nvidia/nemotron-3.5-lightning:free",
    "openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "kc/cohere/north-mini-code:free",
    "openrouter/poolside/laguna-xs-2.1:free",
    "kc/dots-studio/dots-3-note-preview:free",
    "kc/openrouter/free",
]


def main():
    sonuc = {}
    for m in MODELS:
        body = {"model": m, "max_tokens": 200,
                "messages": [{"role": "user", "content": "Sadece OK yaz."}]}
        req = urllib.request.Request(
            BASE, data=json.dumps(body).encode(),
            headers={"Authorization": "Bearer " + KEY,
                     "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                j = json.load(r)
            ch = (j.get("choices") or [{}])
            msg = ch[0].get("message") or {}
            metin = (msg.get("content") or msg.get("reasoning_content")
                     or msg.get("reasoning") or "").strip()
            sonuc[m] = "TAMAM " + repr(metin[:30]) if metin else "BOS"
        except Exception as e:  # noqa: BLE001
            govde = ""
            if hasattr(e, "read"):
                try:
                    govde = e.read().decode("utf-8", "replace")[:100]
                except Exception:  # noqa: BLE001
                    pass
            sonuc[m] = f"HATA {str(e)[:60]} {govde[:60]}"
    with open("_tmp/kilo_test_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)
    for m, s in sonuc.items():
        print(("OK " if s.startswith("TAMAM") else "XX ") + m[:55].ljust(55)
              + s[:50].encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
