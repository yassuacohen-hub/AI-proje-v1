# -*- coding: utf-8 -*-
"""CLAUDE icin combo hiz olcumu (menude 'hizli/yavas' yaziacak, uydurma olmaya).
Kimlik: olculen dogru yol = x-api-key + ANTHROPIC_AUTH_TOKEN (D-380: yazilmaz).
Her combo 2 kez: ilki isi, ikincisi olcum."""
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
S = json.loads((Path.home() / ".claude" / "settings.json").read_text(encoding="utf-8"))
KIMLIK = (S.get("env") or {}).get("ANTHROPIC_AUTH_TOKEN", "")
URL = "http://127.0.0.1:20128/v1/messages"

ADAYLAR = ["claude-claudecombo", "claude_sadece", "fullclaude", "yasu-9router",
           "mimir-dis", "cc/claude-sonnet-5", "cc/claude-opus-5",
           "openrouter/nvidia/nemotron-3.5-lightning:free",
           "bzl/auto:free"]


def at(model: str) -> tuple[str, float]:
    govde = {"model": model, "max_tokens": 48,
             "messages": [{"role": "user", "content": "Say OK"}]}
    t = time.time()
    try:
        req = urllib.request.Request(
            URL, data=json.dumps(govde).encode(),
            headers={"x-api-key": KIMLIK, "anthropic-version": "2023-06-01",
                     "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=180) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return "HATA " + str(e)[:26], time.time() - t
    metin = " ".join([c.get("text", "") for c in (j.get("content") or [])]).strip()
    return (metin[:12] or "BOS"), time.time() - t


print(f"{'MODEL':<52}{'1.DENEME':>10}{'2.DENEME':>10}  SONUC")
for m in ADAYLAR:
    a, ta = at(m)
    b, tb = at(m)
    print(f"{m:<52}{ta:>9.1f}s{tb:>9.1f}s  {a} / {b}")
