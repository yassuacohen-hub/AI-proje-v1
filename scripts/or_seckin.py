# -*- coding: utf-8 -*-
"""Seckin kod modelleri + :batch indirim analizi."""
import json
from pathlib import Path

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = Path(__file__).resolve().parents[1]
RAPOR_DIZIN = KOK / "docs" / "raporlar" / "openrouter"
KATALOG = RAPOR_DIZIN / "or_kod.json"
LOG = RAPOR_DIZIN / "or_seckin.txt"
RAPOR_DIZIN.mkdir(parents=True, exist_ok=True)

if not KATALOG.is_file():
    # Kendi kendine yetmek: katalog yoksa once ureteci calistir.
    # Once %TEMP%'den okuyordu; katalog yoksa dosya hatasi ile sessizce
    # oluyordu. Simdi uretec calistirilir ve katalog garanti edilir.
    import subprocess
    uretec = Path(__file__).resolve().parent / "or_kod_liste.py"
    print("katalog yok, ureteci calistiriliyor: " + str(uretec))
    subprocess.run([sys.executable, "-X", "utf8", str(uretec)],
                   check=True, cwd=str(KOK))

kod = json.loads(KATALOG.read_text(encoding="utf-8"))

d = {r["id"]: r for r in kod}
sat = ["=== SECKIN KOD MODELLERI (deger/performans sirasi) ===",
       f"{'model':<46}{'girdi':>8}{'cikti':>8}{'ctx':>11}  oz", ""]

SECKIN = [
    "deepseek/deepseek-v4-flash",
    "qwen/qwen3-coder-30b-a3b-instruct",
    "deepseek/deepseek-v4.1-flash",
    "openai/gpt-oss-120b",
    "z-ai/glm-5.3-flash",
    "z-ai/glm-5.3",
    "deepseek/deepseek-v3.2",
    "qwen/qwen3.7-flash",
    "anthropic/claude-sonnet-4.5",
    "anthropic/claude-sonnet-4.6",
    "anthropic/claude-opus-4.5",
    "openai/gpt-5.4-mini",
    "openai/gpt-5.4",
    "google/gemini-3-flash-preview",
    "moonshotai/kimi-k2.7-code",
    "x-ai/grok-code-fast-1",
    "mistralai/devstral-2512",
]
for mid in SECKIN:
    r = d.get(mid)
    if not r:
        sat.append(f"{mid:<46}  (bu katalogda yok)")
        continue
    oz = ("+kod" if r["tools"] else "") + ("+reason" if r["reason"] else "")
    sat.append(f"{mid:<46}{r['in']:>8.3f}{r['out']:>8.3f}{r['ctx']:>11,}  {oz}")

# :batch = %50 indirimli ayni model
sat.append("\n=== :batch INDIRIMLI IKIZLER (fiyat/performans kazanci) ===")
sat.append(f"{'model':<46}{'normal':>9}{'batch':>9}{'indirim':>9}")
for mid, r in d.items():
    if not mid.endswith(":batch"):
        continue
    temel = d.get(mid[:-6])
    if not temel:
        continue
    n = temel["in"] * 3 + temel["out"]
    b = r["in"] * 3 + r["out"]
    if b <= 0:
        continue
    ind = (1 - b / n) * 100
    if ind >= 20:
        sat.append(f"{mid[:-6]:<46}{n:>9.3f}{b:>9.3f}%{ind:>8.0f}")

Path(LOG).write_text("\n".join(sat), encoding="utf-8")
print(f"rapor: {LOG} ({len(sat)} satir)")
