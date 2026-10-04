# -*- coding: utf-8 -*-
"""OpenRouter'dan model + fiyat + indirim verisi cek, kod icin en iyileri sirala."""
import json
import os
import re
import urllib.request
from pathlib import Path

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = Path(__file__).resolve().parents[1]
LOG = r"C:\Users\yasin\AppData\Local\Temp\or_pricing.txt"


def env_oku() -> dict:
    yol = KOK / ".env"
    if not yol.exists():
        return {}
    d = {}
    for satir in yol.read_text(encoding="utf-8-sig").splitlines():
        satir = satir.strip()
        if satir and not satir.startswith("#") and "=" in satir:
            k, _, v = satir.partition("=")
            v = v.strip().strip('"').strip("'")
            if v:
                d[k.strip()] = v
    return d


ENV = env_oku()
KEY = ENV.get("OPENROUTER_API_KEY", "")
HDR = {"Authorization": f"Bearer {KEY}"} if KEY else {}


def cek(url: str):
    try:
        req = urllib.request.Request(url, headers=HDR)
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"_hata": f"{type(e).__name__}: {e}"}


raw = cek("https://openrouter.ai/api/v1/models")
front = cek("https://openrouter.ai/api/v1/frontpage/models")

if "_hata" in raw or "_hata" in front:
    Path(LOG).write_text(
        f"raw: {raw.get('_hata', 'ok')}\nfront: {front.get('_hata', 'ok')}\n"
        f"anahtar var mi: {bool(KEY)}",
        encoding="utf-8")
    raise SystemExit(1)

raw_l = {m["id"]: m for m in raw.get("data", [])}
front_l = {m["id"]: m for m in front.get("data", [])}

sat = [f"raw model: {len(raw_l)} | frontpage model: {len(front_l)}", ""]

# Kod icin guclu sayilan model aileleri (isimden eslesme)
KOD = re.compile(
    r"claude|codex|coder|gpt-5|gpt-oss|deepseek|qwen|kimi|glm|gemini|"
    r"grok|minimax|mistral|devstral|starcoder|codestral",
    re.I)

sat.append("=== INDIRIMLI MODELLER (frontpage < raw) ===")
indirimli = []
for mid, m in front_l.items():
    if mid not in raw_l:
        continue
    fp = m.get("pricing") or {}
    rp = raw_l[mid].get("pricing") or {}
    try:
        f_in = float(fp.get("prompt") or 0)
        r_in = float(rp.get("prompt") or 0)
    except (TypeError, ValueError):
        continue
    if r_in > 0 and f_in < r_in:
        indirim = (1 - f_in / r_in) * 100
        if indirim >= 20:
            indirimli.append((indirim, mid, r_in, f_in))

indirimli.sort(reverse=True)
for yuzde, mid, ri, fi in indirimli[:40]:
    sat.append(f"  %{yuzde:5.1f} indirim  {mid:52} "
               f"girdi ${ri:.4f} -> ${fi:.4f} /M tok")

Path(LOG).write_text("\n".join(sat), encoding="utf-8")
json.dump(
    [{"id": mid, "indirim": round(y, 1), "raw": ri, "front": fi}
     for y, mid, ri, fi in indirimli],
    open(r"C:\Users\yasin\AppData\Local\Temp\or_indirimli.json", "w",
         encoding="utf-8"), ensure_ascii=False, indent=1)
