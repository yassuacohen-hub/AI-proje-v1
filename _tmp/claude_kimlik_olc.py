# -*- coding: utf-8 -*-
"""CLAUDE 401'in kokunu ve Desktop'un model listesi kaynagini olcer.
Anahtar degerleri YAZILMAZ (D-380) - yalniz son 4 hane + basari durumu."""
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
S = json.loads((Path.home() / ".claude" / "settings.json").read_text(encoding="utf-8"))
env = S.get("env", {})

print("[1] Kullanilabilir anahtarlar (son 4 hane)")
ADAYLAR = []
for k in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
    v = env.get(k)
    if v:
        ADAYLAR.append((f"settings:{k}", v))
print("  " + " · ".join(f"{a}=***{b[-4:]}" for a, b in ADAYLAR))

print("\n[2] Ayni combo, iki kimlik bicimiyle (/v1/messages)")
for baslik, model in [("claude-claudecombo", "claude-claudecombo"),
                      ("fullclaude", "fullclaude"),
                      ("cc/claude-sonnet-5", "cc/claude-sonnet-5")]:
    govde = {"model": model, "max_tokens": 48,
             "messages": [{"role": "user", "content": "Say CLAUDE-OK"}]}
    for kimlik, deger in ADAYLAR:
        for hbicim, h in (("x-api-key", {"x-api-key": deger,
                                         "anthropic-version": "2023-06-01"}),
                          ("Bearer", {"Authorization": "***" + deger,
                                      "anthropic-version": "2023-06-01"})):
            req = urllib.request.Request("http://127.0.0.1:20128/v1/messages",
                                         data=json.dumps(govde).encode(),
                                         headers={**h, "Content-Type": "application/json"},
                                         method="POST")
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    j = json.loads(r.read().decode("utf-8", "replace"))
                metin = " ".join([c.get("text", "") for c in (j.get("content") or [])]).strip()
                print(f"  OK   {baslik:<20}{kimlik:<24}{hbicim:<10}{metin[:22] or 'BOS'}")
            except Exception as e:  # noqa: BLE001
                print(f"  hata {baslik:<20}{kimlik:<24}{hbicim:<10}{str(e)[:26]}")

print("\n[3] Claude Desktop 'Gateway' modeli nerede tanimli?")
for p in [Path.home() / "AppData/Roaming/Claude/config.json",
          Path.home() / "AppData/Roaming/Claude/configLibrary",
          Path.home() / "AppData/Local/Claude",
          Path.home() / ".claude/daemon"]:
    print(f"  {'VAR' if p.exists() else 'yok':<5}{p}")

print("\n[4] Sistem kullanci ortami ANTHROPIC degiskenleri")
o = subprocess.run(["cmd", "/c", "set"], capture_output=True, text=True,
                   encoding="utf-8", errors="replace", timeout=30)
satirlar = [s for s in o.stdout.splitlines() if "ANTHROPIC" in s.upper()]
for s in satirlar:
    ad, _, deger = s.partition("=")
    print(f"  {ad:<34}{'***' + deger[-4:] if 'KEY' in ad or 'TOKEN' in ad else deger[:56]}")

print("\n[5] 9Router Anthropic-bicimli model listesi (Desktop buna bakar mi?)")
for yol in ("/v1/models", "/v1/models?provider=claude", "/v1beta/models"):
    deger = env.get("ANTHROPIC_AUTH_TOKEN") or ""
    req = urllib.request.Request("http://127.0.0.1:20128" + yol,
                                 headers={"Authorization": "***" + deger})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
        ver = j.get("data") or j.get("models") or []
        print(f"  {yol:<28}{len(ver)} kayit · ornek: {[m.get('id') or m.get('name') for m in ver[:3]]}")
    except Exception as e:  # noqa: BLE001
        print(f"  {yol:<28}HATA {str(e)[:40]}")
