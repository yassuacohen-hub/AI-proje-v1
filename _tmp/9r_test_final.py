#!/usr/bin/env python3
"""9Router combo'larini canli test et + VS Code ayar dosyalarini dogrula."""
import json
import urllib.error
import urllib.request
from pathlib import Path

KEY = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
URL = "http://localhost:20128/v1/chat/completions"

print("=== 1) Ayar dosyalari dogrulama ===")
for p in [
    ".vscode/settings.json",
    "C:/Users/yasin/AppData/Roaming/Code/User/settings.json",
]:
    try:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        models = d.get("github.copilot.chat.customOaiModels", [])
        print(f"[OK] {p} -> {len(models)} combo")
        for m in models:
            print(f"     - {m.get('name')} | model={m.get('model')} | {m.get('url')}")
    except Exception as e:
        print(f"[HATA] {p}: {e}")

print("\n=== 2) 9Router canli combo testi ===")
for model in ["yasu-9router", "fullclaude", "claude-claudecombo", "claude_sadece", "mimir-dis"]:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Tek kelimeyle yanitla: calisiyor mu?"}],
        "max_tokens": 20,
    }).encode("utf-8")
    req = urllib.request.Request(
        URL, data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            d = json.loads(r.read().decode("utf-8"))
            ch = d.get("choices") or [{}]
            msg = (ch[0].get("message") or {}).get("content", "")
            usage = d.get("usage") or {}
            print(f"[OK] {model:22s} -> {str(msg)[:60]!r} | in={usage.get('prompt_tokens')} out={usage.get('completion_tokens')}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {model}: {e.read().decode('utf-8','ignore')[:200]}")
    except Exception as e:
        print(f"[HATA] {model}: {e}")

print("\n=== 3) 9Router /v1/models (combo gorunumu) ===")
try:
    req = urllib.request.Request(
        "http://localhost:20128/v1/models",
        headers={"Authorization": f"Bearer {KEY}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode("utf-8"))
        ids = [x.get("id") for x in (d.get("data") or [])]
        combos = [i for i in ids if i in {
            "yasu-9router", "fullclaude", "claude-claudecombo",
            "claude_sadece", "mimir-dis", "fetch-combo", "search-combo",
        }]
        print(f"[OK] toplam model={len(ids)} | combo olarak gorunenler={combos}")
except Exception as e:
    print(f"[HATA] {e}")
