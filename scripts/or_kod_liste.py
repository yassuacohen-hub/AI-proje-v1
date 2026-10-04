# -*- coding: utf-8 -*-
"""OpenRouter kod modelleri: fiyat + indirim + deger analizi."""
import json
import re
import urllib.request
from pathlib import Path

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = Path(__file__).resolve().parents[1]
#: Rapor + katalog repo icinde yazilir. once %TEMP%'e yaziliyordu; Temp
#: temizlenince betik sessizce olurdu (dosya bulunamadi hatasi).
RAPOR_DIZIN = KOK / "docs" / "raporlar" / "openrouter"
LOG = RAPOR_DIZIN / "or_kod.txt"
KATALOG = RAPOR_DIZIN / "or_kod.json"
RAPOR_DIZIN.mkdir(parents=True, exist_ok=True)

env = (KOK / ".env").read_text(encoding="utf-8-sig")
KEY = next(l.split("=", 1)[1].strip().strip('"')
           for l in env.splitlines() if l.startswith("OPENROUTER_API_KEY"))

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {KEY}"})
models = json.loads(urllib.request.urlopen(req, timeout=45).read().decode())["data"]

sat = [f"OpenRouter toplam model: {len(models)}", ""]

rows = []
for m in models:
    p = m.get("pricing") or {}
    try:
        pin = float(p.get("prompt") or 0) * 1_000_000
        pout = float(p.get("completion") or 0) * 1_000_000
    except (TypeError, ValueError):
        continue
    if pin <= 0 and pout <= 0:
        continue  # ucretsiz olanlar ayri
    ctx = m.get("context_length") or 0
    rows.append({
        "id": m["id"],
        "name": m.get("name") or m["id"],
        "in": pin,
        "out": pout,
        "ctx": ctx,
        "cache": float(p.get("input_cache_read") or 0) * 1_000_000,
        "tools": "tools" in (m.get("supported_parameters") or []),
        "reason": bool(m.get("reasoning")),
    })

# Kod icin ilgili olanlar
KOD = re.compile(
    r"claude|codex|coder|gpt-5|gpt-6|gpt-oss|deepseek|qwen|kimi|glm|"
    r"gemini|grok|minimax|mistral|devstral|granite", re.I)

kod = [r for r in rows if KOD.search(r["id"])]
sat.append(f"Ucretli model: {len(rows)} | kod ilgili: {len(kod)}")

# ucuzdan pahaliya (blended fiyat: 3 input + 1 output)
for r in kod:
    r["harman"] = r["in"] * 3 + r["out"]

kod.sort(key=lambda x: x["harman"])

sat.append("\n=== EN UCUZ KOD MODELLERI (harman: 3 girdi + 1 cikti, $/M tok) ===")
sat.append(f"{'model':<46}{'girdi':>8}{'cikti':>8}{'harman':>9}{'ctx':>9}  oz")
for r in kod[:35]:
    oz = ("+kod" if r["tools"] else "") + ("+reason" if r["reason"] else "")
    sat.append(f"{r['id']:<46}{r['in']:>8.3f}{r['out']:>8.3f}"
               f"{r['harman']:>9.3f}{r['ctx']:>9,}  {oz}")

Path(LOG).write_text("\n".join(sat), encoding="utf-8")
KATALOG.write_text(json.dumps(kod, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
print(f"rapor : {LOG}")
print(f"katalog: {KATALOG} ({len(kod)} model)")
