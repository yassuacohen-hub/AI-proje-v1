# -*- coding: utf-8 -*-
"""EVREN/CODEX MODELLERI CLAUDE'DA CALISIYOR MU? (PO istegi: 'onlari da ekle')
Neden ayri test: ham /v1/messages testinde nemotron BOS dondu, ama Claude Code
ile ayni id CALISTI (olculen) -> Claude Code'un govdemi farkli. Kanit olcusu:
`claude --model X -p --output-format json` -> result metni + modelUsage anahtari.
2 tekrar: ikisi de metin ureten adaylar listeye girer. Anahtar yazilmaz (D-380)."""
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

ADAYLAR = [
    ("EVREN hizli", "qwen3.8-flash-next"),
    ("EVREN guclu-b", "deepseek-v4.1-flash"),
    ("EVREN derin", "glm-5.3"),
    ("CODEX guclu", "cx/gpt-5.6-luna"),
    ("CODEX kod", "cx/gpt-5.6-terra"),
    ("BEDAVA hizli", "openrouter/nvidia/nemotron-3.5-lightning:free"),
    ("BEDAVA derin", "openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"),
    ("BEDAVA oto", "bzl/auto:free"),
    ("EVREN ultra", "cl/nvidia/nemotron-3-ultra-550b-a55b:free"),
    ("ALIAS luna", "gpt-5.6-luna"),
]
TEKRAR = 2


def tek(model: str) -> tuple[bool, float, str]:
    t = time.time()
    try:
        o = subprocess.run(["claude", "--model", model, "-p",
                            "Reply with exactly: EVREN-OK",
                            "--output-format", "json"],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=200)
    except Exception as e:  # noqa: BLE001
        return False, time.time() - t, "CALISTIRMA " + str(e)[:34]
    sn = time.time() - t
    try:
        j = json.loads((o.stdout or "").strip())
    except Exception:
        return False, sn, "JSON-degil " + ((o.stdout or o.stderr) or "")[:40]
    kullanilan = list((j.get("modelUsage") or {}).keys())
    metin = str(j.get("result") or "")
    ok = ("EVREN-OK" in metin) or (bool(metin.strip()) and not j.get("is_error"))
    return ok, sn, f"{kullanilan} · {metin[:16] or 'BOS'}"


print(f"{'ETIKET':<14}{'MODEL':<56}{'ISABET':>7}  AYRINT")
iyi = []
for etiket, model in ADAYLAR:
    sonuc = [tek(model) for _ in range(TEKRAR)]
    isabet = sum(1 for ok, _, _ in sonuc if ok)
    en_kotu = max(sn for _, sn, _ in sonuc)
    detay = sonuc[0][2]
    if isabet == TEKRAR:
        iyi.append((etiket, model, round(en_kotu, 1)))
    print(f"{etiket:<14}{model:<56}{isabet}/{TEKRAR}   {en_kotu:5.1f}s {detay}")

print("\nCLAUDE PORTFOYUNE GIRECEKLER (2/2):")
for e, m, sn in iyi:
    print(f"  {e:<14}{m:<56}{sn:>5.1f}s")
Path(r"c:\Huginn Data Projesi\_tmp\claude_evren_iyi.json").write_text(
    json.dumps(iyi, ensure_ascii=False), encoding="utf-8")
print("\nkayit: _tmp/claude_evren_iyi.json")
