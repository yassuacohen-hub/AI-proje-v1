# -*- coding: utf-8 -*-
"""KRITIK BULGU: sistem ortaminda ANTHROPIC_BASE_URL = http://127.0.0.1:8045/
yani Claude Desktop 9Router'a (20128) DEGIL, 8045'e gidiyor. 401'in sebebi bu
olabilir. Olculecek:
 1) 8045 ne? (banner / saglayici imzasi)
 2) 8045 /v1/messages'i combo ile kabul ediyor mu (canli PONG)
 3) Claude Code ayarindaki 20128 ile Desktop'in 8045'i ayni sey mi
Anahtar degerleri YAZILMAZ (D-380)."""
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
S = json.loads((Path.home() / ".claude" / "settings.json").read_text(encoding="utf-8"))
ENV = S.get("env", {})
ORTAM_URL = os.environ.get("ANTHROPIC_BASE_URL", "?")
print(f"[0] Desktop'in gittigi yer: {ORTAM_URL}")
print(f"    Claude Code ayari     : {ENV.get('ANTHROPIC_BASE_URL')}")

for port in (8045, 20128):
    taban = f"http://127.0.0.1:{port}"
    print(f"\n=== PORT {port} ===")
    for yol in ("", "/v1/models"):
        try:
            with urllib.request.urlopen(taban + yol, timeout=15) as r:
                v = r.read(300).decode("utf-8", "replace")
            print(f"  GET {yol or '/':<12}-> {v[:120]!r}")
        except Exception as e:  # noqa: BLE001
            print(f"  GET {yol or '/':<12}-> {str(e)[:60]}")

    govde = {"model": "claude-claudecombo", "max_tokens": 48,
             "messages": [{"role": "user", "content": "Say CLAUDE-OK"}]}
    for etiket, anahtar in (("API_KEY", ENV.get("ANTHROPIC_API_KEY", "")),
                            ("AUTH_TOKEN", ENV.get("ANTHROPIC_AUTH_TOKEN", ""))):
        if not anahtar:
            continue
        for hb in ("x-api-key", "bearer"):
            h = {"anthropic-version": "2023-06-01", "Content-Type": "application/json"}
            h.update({"x-api-key": anahtar} if hb == "x-api-key"
                     else {"Authorization": "***" + anahtar})
            try:
                req = urllib.request.Request(taban + "/v1/messages",
                                             data=json.dumps(govde).encode(),
                                             headers=h, method="POST")
                with urllib.request.urlopen(req, timeout=120) as r:
                    j = json.loads(r.read().decode("utf-8", "replace"))
                m = " ".join([c.get("text", "") for c in (j.get("content") or [])]).strip()
                print(f"  POST /v1/messages {etiket:<11}{hb:<9}OK  -> {m[:24] or 'BOS'}")
            except Exception as e:  # noqa: BLE001
                print(f"  POST /v1/messages {etiket:<11}{hb:<9}hata-> {str(e)[:34]}")
