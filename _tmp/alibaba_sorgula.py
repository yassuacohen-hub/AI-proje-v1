#!/usr/bin/env python3
"""Alibaba Cloud Claude API endpoint'ini sorgula: modeller + chat testi."""
import json, urllib.request, urllib.error

BASE = "https://ws-jq8d6ivxtery2epw.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"
KEY = "sk-ws-H.DIDEYLD.qttz.MEUCIGXvSSUdJ0ml09hIPGI-uv5IMVsk3BPDK7KuhXREuqY5AiEA9KiKuuUzknw9FVSmTuO1FkWNVP7IIRjNVApMJ4oZ-2A"


def _get(path: str) -> dict:
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_body": e.read().decode("utf-8", "ignore")[:500]}
    except Exception as e:
        return {"_err": str(e)}


def _post(path: str, payload: dict) -> dict:
    url = f"{BASE}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_body": e.read().decode("utf-8", "ignore")[:800]}
    except Exception as e:
        return {"_err": str(e)}


print("=== /models ===")
m = _get("/models")
print(json.dumps(m, ensure_ascii=False, indent=2)[:3000])

print("\n=== chat test (claude sonnet) ===")
c = _post("/chat/completions", {
    "model": "claude-sonnet-4-5-20250929",
    "messages": [{"role": "user", "content": "Tek kelimeyle yanitla: calisiyor mu?"}],
    "max_tokens": 20,
})
print(json.dumps(c, ensure_ascii=False, indent=2)[:2000])

print("\n=== chat test (claude opus) ===")
c2 = _post("/chat/completions", {
    "model": "claude-opus-4-5-20251101",
    "messages": [{"role": "user", "content": "Tek kelimeyle yanitla: calisiyor mu?"}],
    "max_tokens": 20,
})
print(json.dumps(c2, ensure_ascii=False, indent=2)[:2000])