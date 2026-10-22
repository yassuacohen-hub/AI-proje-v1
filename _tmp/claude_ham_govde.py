# -*- coding: utf-8 -*-
"""Claude Pro ham yanıt gövdesi — ayrıştırıcı mı kör, model mi boş dönüyor ayır et."""
import json
import urllib.request

KEY9 = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"


def ham(url, body):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY9,
                 "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return "HTTP200", r.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        g = ""
        if hasattr(e, "read"):
            try:
                g = e.read().decode("utf-8", "replace")
            except Exception:  # noqa: BLE001
                pass
        return "HATA", str(e) + " || " + g


U = "http://localhost:20128/v1"
for ad, url, gov in [
    ("responses/fullclaude", U + "/responses",
     {"model": "fullclaude", "input": "Reply with exactly: CLAUDE-AYAKTA", "stream": False}),
    ("chat/fullclaude", U + "/chat/completions",
     {"model": "fullclaude", "max_tokens": 200,
      "messages": [{"role": "user", "content": "Reply with exactly: CLAUDE-AYAKTA"}]}),
    ("chat/opus5", U + "/chat/completions",
     {"model": "cc/claude-opus-5", "max_tokens": 200,
      "messages": [{"role": "user", "content": "Reply with exactly: CLAUDE-AYAKTA"}]}),
]:
    st, metin = ham(url, gov)
    print("=" * 20, ad, st)
    print(metin[:700].encode("ascii", "replace").decode())
    with open("_tmp/claude_ham.txt", "a", encoding="utf-8") as f:
        f.write("\n===== " + ad + " " + st + "\n" + metin[:1500])
