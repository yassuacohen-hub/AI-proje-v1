# -*- coding: utf-8 -*-
"""CLAUDE Code'da gercek model secimi mumkun mu? (PO'nun istegi)
Kanit: `claude --model <combo> -p "..."` -> cevap gelirse SECIM VAR.
3 model denenir: claude-claudecombo, cc/claude-sonnet-5, openrouter nemotron free.
Not: Claude Code ayarindaki env (ANTHROPIC_*) CLAUDE_CODE_SSE_PORT vb. ile okunur;
bu yuzden env'i os.environ'a yukleyip calistiriyoruz (settings.json'daki env)."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
S = json.loads((Path.home() / ".claude" / "settings.json").read_text(encoding="utf-8"))
for k, v in (S.get("env") or {}).items():
    os.environ[k] = str(v)

ADAYLAR = ["claude-claudecombo", "cc/claude-sonnet-5",
           "openrouter/nvidia/nemotron-3.5-lightning:free"]

for model in ADAYLAR:
    t = time.time()
    try:
        o = subprocess.run(["claude", "--model", model, "-p",
                            "Reply with exactly: SECIM-OK"],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
        sn = time.time() - t
        cikti = (o.stdout or "").strip()
        hata = (o.stderr or "").strip()
        durum = "OK" if "SECIM-OK" in cikti else "hata"
        print(f"{durum:<5}{sn:6.1f}s  {model}")
        if durum == "OK":
            print(f"      cevap: {cikti[:70]!r}")
        else:
            print(f"      stdout: {cikti[:90]!r}")
            print(f"      stderr: {hata[:150]!r}")
    except FileNotFoundError:
        print("claude CLI BULUNAMADI (PATH'te yok)")
        break
    except Exception as e:  # noqa: BLE001
        print(f"hata  {time.time() - t:6.1f}s  {model} -> {str(e)[:80]}")
