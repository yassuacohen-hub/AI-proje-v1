# -*- coding: utf-8 -*-
"""HIZ OLCUMU v2: sunucu 'Extra data' donuyor = govde tek JSON degil (NDJSON/parcali).
Cozum: ham metinde metin parcasini regex ile bul; sure yine olculur.
Kimlik: x-api-key + ANTHROPIC_AUTH_TOKEN (olculen dogru yol). Deger yazilmaz."""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
S = json.loads((Path.home() / ".claude" / "settings.json").read_text(encoding="utf-8"))
KIMLIK = (S.get("env") or {}).get("ANTHROPIC_AUTH_TOKEN", "")
URL = "http://127.0.0.1:20128/v1/messages"

ADAYLAR = ["claude-claudecombo", "fullclaude", "claude_sadece", "mimir-dis",
           "yasu-9router", "cc/claude-sonnet-5", "cc/claude-opus-5",
           "cc/claude-haiku-4-5-20251001",
           "openrouter/nvidia/nemotron-3.5-lightning:free", "bzl/auto:free"]


def at(model: str) -> tuple[float, str]:
    govde = {"model": model, "max_tokens": 48,
             "messages": [{"role": "user", "content": "Say OK"}]}
    t = time.time()
    try:
        req = urllib.request.Request(
            URL, data=json.dumps(govde).encode(),
            headers={"x-api-key": KIMLIK, "anthropic-version": "2023-06-01",
                     "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=180) as r:
            ham = r.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return time.time() - t, "HATA " + str(e)[:22]
    parca = re.findall(r'"text"\s*:\s*"([^"]{1,40})"', ham)
    return time.time() - t, (parca[0][:16] if parca else "BOS")


print(f"{'MODEL':<50}{'1.':>7}{'2.':>7}  SONUC")
sonuc = {}
for m in ADAYLAR:
    t1, a = at(m)
    t2, b = at(m)
    sonuc[m] = (t1, t2)
    print(f"{m:<50}{t1:>6.1f}s{t2:>6.1f}s  {a} / {b}")

print("\nORNEK HAM (ilk model, 300b):")
govde = {"model": ADAYLAR[0], "max_tokens": 24,
         "messages": [{"role": "user", "content": "Say OK"}]}
req = urllib.request.Request(URL, data=json.dumps(govde).encode(),
                             headers={"x-api-key": KIMLIK,
                                      "anthropic-version": "2023-06-01",
                                      "Content-Type": "application/json"},
                             method="POST")
with urllib.request.urlopen(req, timeout=120) as r:
    print(repr(r.read(300).decode("utf-8", "replace")))
