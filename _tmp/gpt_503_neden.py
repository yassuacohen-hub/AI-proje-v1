# -*- coding: utf-8 -*-
"""cx/ GPT combo'lari neden 503 veriyor? Govdeyi tam yazar. Anahtar yazilmaz."""
import json
import pathlib
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
K = str((json.loads((pathlib.Path.home() / ".claude" / "settings.json")
                    .read_text(encoding="utf-8")).get("env") or {})
        .get("ANTHROPIC_AUTH_TOKEN") or "")
for m in ("claude-gpt-6-sol", "claude-gpt-6-luna", "claude-gpt-56-sol",
          "claude-gpt-6-astra", "claude-gpt-61-sol", "claude-gpt-56-terra"):
    b = json.dumps({"model": m, "max_tokens": 20, "messages": [
        {"role": "user", "content": "de ki: tamam"}]}).encode()
    r = urllib.request.Request(
        "http://127.0.0.1:20128/v1/messages", data=b,
        headers={"Authorization": "Bearer " + K,
                 "content-type": "application/json",
                 "anthropic-version": "2023-06-01"})
    try:
        print(m, "OK", urllib.request.urlopen(r, timeout=90).read().decode("utf-8")[:140])
    except urllib.error.HTTPError as e:
        print(m, e.code, e.read().decode("utf-8")[:380])
    except Exception as e:  # noqa: BLE001
        print(m, "HATA", str(e)[:80])
