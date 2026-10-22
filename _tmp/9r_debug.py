#!/usr/bin/env python3
import json, urllib.request, urllib.error

KEY = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
BASE = "http://localhost:20128"

print("=== GET /v1/models ===")
try:
    with urllib.request.urlopen(urllib.request.Request(
        f"{BASE}/v1/models",
        headers={"Authorization": f"Bearer {KEY}"}
    ), timeout=30) as r:
        print("status:", r.status)
        ct = r.headers.get("content-type", "")
        print("content-type:", ct)
        body = r.read().decode("utf-8", "ignore")[:500]
        print("body start:", body)
except Exception as e:
    print("ERROR:", e)

print("\n=== POST /v1/chat/completions minimal ===")
try:
    data = json.dumps({
        "model": "yasu-9router",
        "messages": [{"role": "user", "content": "hello"}],
        "max_tokens": 5,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        print("status:", r.status)
        print("headers:", dict(r.headers))
        body = r.read().decode("utf-8", "ignore")
        print("body:", body[:500])
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code, e.read().decode("utf-8", "ignore")[:500])
except Exception as e:
    print("ERROR:", e)
