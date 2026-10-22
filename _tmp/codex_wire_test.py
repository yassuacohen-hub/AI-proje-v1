# -*- coding: utf-8 -*-
"""Codex wire_api seçimi: /responses ucu acik mi? (9Router + Evren)"""
import json
import urllib.request

TESTS = [
    ("9R-responses", "http://localhost:20128/v1/responses",
     "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44", "openrouter/openrouter/free"),
    ("9R-chat", "http://localhost:20128/v1/chat/completions",
     "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44", "openrouter/nvidia/nemotron-3.5-lightning:free"),
    ("evren-responses", "https://evren-llmapi.ssyz.org.tr/v1/responses",
     "evren_llm_BZ2d6Zxirtse1n5ehKgLDp_3h4LVnSXCJBc3BYWD70M", "glm-5.3"),
    ("evren-chat", "https://evren-llmapi.ssyz.org.tr/v1/chat/completions",
     "evren_llm_BZ2d6Zxirtse1n5ehKgLDp_3h4LVnSXCJBc3BYWD70M", "glm-5.3"),
]


def post(url, key, body):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return "OK " + str(r.status)
    except Exception as e:  # noqa: BLE001
        govde = ""
        if hasattr(e, "read"):
            try:
                govde = e.read().decode("utf-8", "replace")[:120]
            except Exception:  # noqa: BLE001
                pass
        return f"HATA {type(e).__name__}: {str(e)[:80]} {govde[:80]}"


def main():
    for ad, url, key, model in TESTS:
        if "/responses" in url:
            body = {"model": model, "input": "Say OK", "stream": False}
        else:
            body = {"model": model, "max_tokens": 8,
                    "messages": [{"role": "user", "content": "Say OK"}]}
        print((ad + " " * 20)[:20], post(url, key, body).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
