# -*- coding: utf-8 -*-
import json
from pathlib import Path

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = Path(__file__).resolve().parents[1]
SABLON = KOK / "docs" / "continue_config.json"
cfg = json.loads(SABLON.read_text(encoding="utf-8-sig"))
modeller = cfg["models"]

OR_BASE = "https://openrouter.ai/api/v1"
OR_KEY = "${env:OPENROUTER_API_KEY}"

# 2026-10-01 OpenRouter /models analizi: 462 model, 278 kod ilgili.
# Fiyat = $/M token (girdi/cikti). harman = 3 girdi + 1 cikti.
# :batch = ayni modelin %50-75 indirimli ikizi (asynchronous, daha yavas).
YENI = [
    # --- En iyi deger / performans (SWE-bench sinifi kodlama) ---
    ("[UCRETLI] OR · DeepSeek V4 Flash (0.04/0.08 · EN UCUZ + 1M ctx)", "deepseek/deepseek-v4-flash", 1048576),
    ("[UCRETLI] OR · DeepSeek V4.1 Flash (0.03/0.60 · 1M ctx)", "deepseek/deepseek-v4.1-flash", 1048576),
    ("[UCRETLI] OR · Qwen3 Coder 30B (0.07/0.28 · saf kod)", "qwen/qwen3-coder-30b-a3b-instruct", 262144),
    ("[UCRETLI] OR · GPT-OSS 120B (0.04/0.17 · acik agirlik)", "openai/gpt-oss-120b", 131072),
    ("[UCRETLI] OR · Qwen3.7 Flash (0.03/0.13 · 1M ctx)", "qwen/qwen3.7-flash", 1000000),
    ("[UCRETLI] OR · GLM 5.3 Flash (0.15/0.50 · 1M ctx)", "z-ai/glm-5.3-flash", 1048576),
    ("[UCRETLI] OR · DeepSeek V3.2 (0.28/0.42 · akil yurutme)", "deepseek/deepseek-v3.2", 163840),
    ("[UCRETLI] OR · Kimi K2.7 Code (0.67/3.35 · uzun baglam)", "moonshotai/kimi-k2.7-code", 262144),
    ("[UCRETLI] OR · Devstral 2512 (0.40/2.00 · Mistral kod)", "mistralai/devstral-2512", 262144),
    ("[UCRETLI] OR · Gemini 3 Flash (0.50/3.00 · 1M ctx)", "google/gemini-3-flash-preview", 1048576),
    # --- %50 indirimli :batch ikizleri (ayni model, yari fiyat) ---
    ("[UCRETLI %50] OR · DeepSeek V4 Flash :batch", "deepseek/deepseek-v4-flash:batch", 1048576),
    ("[UCRETLI %50] OR · Qwen3 Coder 30B :batch", "qwen/qwen3-coder-30b-a3b-instruct:batch", 262144),
    ("[UCRETLI %50] OR · GLM 5.3 Flash :batch (%60)", "z-ai/glm-5.3-flash:batch", 1048576),
    ("[UCRETLI %50] OR · Gemini 3 Flash :batch", "google/gemini-3-flash-preview:batch", 1048576),
    ("[UCRETLI %50] OR · Claude Sonnet 4.5 :batch (24 -> 12)", "anthropic/claude-sonnet-4.5:batch", 1000000),
    ("[UCRETLI %50] OR · Claude Opus 4.5 :batch (40 -> 20)", "anthropic/claude-opus-4.5:batch", 200000),
]

mevcut = {m.get("model") for m in modeller}
eklenen = 0
for baslik, slug, ctx in YENI:
    if slug in mevcut:
        continue
    modeller.append({
        "title": baslik,
        "provider": "openrouter",
        "model": slug,
        "apiBase": OR_BASE,
        "apiKey": OR_KEY,
        "contextLength": ctx,
    })
    eklenen += 1

# Sirala: ucretsizler once, sonra ucuz ucretli, en sonda pahali
UCR = "[UCRETSIZ]"
YER = "[YEREL]"


def anahtar(m):
    t = m.get("title", "")
    if t.startswith(UCR):
        return (0, 0)
    if t.startswith(YER):
        return (1, 0)
    # ucretli: batch olanlar daha ucuz -> onlar once
    return (2, 0 if ":batch" in t else 1)


modeller.sort(key=anahtar)

SABLON.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n",
                  encoding="utf-8")
print(f"Eklenen: {eklenen}")
print(f"Toplam: {len(modeller)}\n")
for i, m in enumerate(modeller, 1):
    print(f"  {i:2d}. {m['title']}")
