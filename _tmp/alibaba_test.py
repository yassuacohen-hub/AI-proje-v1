#!/usr/bin/env python3
import json, urllib.request, urllib.error

KEY = "sk-ws-H.DIDEYLD.qttz.MEUCIGXvSSUdJ0ml09hIPGI-uv5IMVsk3BPDK7KuhXREuqY5AiEA9KiKuuUzknw9FVSmTuO1FkWNVP7IIRjNVApMJ4oZ-2A"
BASE = "https://ws-jq8d6ivxtery2epw.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"

def get_json(path):
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {KEY}",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_body": e.read().decode("utf-8", "ignore")[:500]}
    except Exception as e:
        return {"_err": str(e)}

def post_chat(model, message):
    url = f"{BASE}/chat/completions"
    data = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 20,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            # Handle streaming? Assume non-streaming for simplicity
            resp = r.read().decode("utf-8")
            return json.loads(resp)
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_body": e.read().decode("utf-8", "ignore")[:500]}
    except Exception as e:
        return {"_err": str(e)}

print("=== /models ===")
models = get_json("/models")
print(json.dumps(models, ensure_ascii=False, indent=2)[:2000])

# Extract model ids if possible
if isinstance(models, dict) and "data" in models:
    ids = [m.get("id") for m in models["data"] if isinstance(m, dict)]
    print(f"\nFound {len(ids)} models. First 10: {ids[:10]}")
    # Look for Claude-like models
    claude_ids = [i for i in ids if "claude" in i.lower()]
    print(f"Claude-related models: {claude_ids[:10]}")
else:
    print("Could not parse models list.")

print("\n=== Chat test (first Claude model if any) ===")
if isinstance(models, dict) and "data" in models:
    ids = [m.get("id") for m in models["data"] if isinstance(m, dict)]
    claude_ids = [i for i in ids if "claude" in i.lower()]
    if claude_ids:
        test_model = claude_ids[0]
        print(f"Testing model: {test_model}")
        resp = post_chat(test_model, "Tek kelimeyle yanıt ver: çalışıyor mu?")
        print(json.dumps(resp, ensure_ascii=False, indent=2)[:1000])
    else:
        print("No Claude model found; testing first model if any.")
        if ids:
            test_model = ids[0]
            print(f"Testing model: {test_model}")
            resp = post_chat(test_model, "Tek kelimeyle yanıt ver: çalışıyor mu?")
            print(json.dumps(resp, ensure_ascii=False, indent=2)[:1000])
else:
    print("Skipping chat test due to missing models.")