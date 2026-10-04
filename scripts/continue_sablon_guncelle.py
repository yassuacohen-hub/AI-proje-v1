# -*- coding: utf-8 -*-
"""Continue sablonunu guncelle: tara, sirala, calismayanlari cikar."""
import json
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
SABLON = KOK / "docs" / "continue_config.json"

cfg = json.loads(SABLON.read_text(encoding="utf-8-sig"))
modeller = cfg["models"]
print("Sablondaki mevcut model:", len(modeller))

# --- Calismayan modeller (2026-10-01 canli POST testi) ---
CALISMAYAN = {
    # 404: "unavailable for free" - Nex artik ucretli
    "nex-agi/nex-n2.5-pro:free",
    "nex-agi/nex-n2.5-mini:free",
    # 403: "Access denied" - Groq hesabinda erisim yok
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
}

# --- Taramadan bulunan, testi gecen YENI modeller (2026-10-01) ---
YENI = [
    {
        "title": "[UCRETSIZ] OR · Ling 3.0 Flash (hizli, ucuz katman)",
        "provider": "openrouter",
        "model": "inclusionai/ling-3.0-flash-sante:free",
        "apiBase": "https://openrouter.ai/api/v1",
        "apiKey": "${env:OPENROUTER_API_KEY}",
        "contextLength": 131072,
    },
    {
        "title": "[UCRETSIZ] OR · Nemotron 3.5 Content Safety (ozel gorev)",
        "provider": "openrouter",
        "model": "nvidia/nemotron-3.5-content-safety:free",
        "apiBase": "https://openrouter.ai/api/v1",
        "apiKey": "${env:OPENROUTER_API_KEY}",
        "contextLength": 131072,
    },
    {
        "title": "[UCRETSIZ] OR · Laguna XS 2.1 (kod odakli, hafif)",
        "provider": "openrouter",
        "model": "poolside/laguna-xs-2.1:free",
        "apiBase": "https://openrouter.ai/api/v1",
        "apiKey": "${env:OPENROUTER_API_KEY}",
        "contextLength": 131072,
    },
]

# --- Siralama: iyiden kotuye (asagidaki sirali liste temel alinir) ---
# Puanlama: model adindaki guc sinyalleri + ctx + onceden dogrulanmis durum
SIRALAMA = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",   # 550B, 1M ctx - en guclu
    "nvidia/nemotron-3-super-120b-a12b:free",   # 120B
    "cohere/north-mini-code:free",              # kod odakli
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",  # reasoning
    "nvidia/nemotron-3.5-lightning-30b-a3b",    # NVIDIA dogrudan, en hizli
    "nvidia/nemotron-3.5-lightning:free",       # 1M ctx
    "dots-studio/dots-3-note-preview:free",     # 512k ctx
    "poolside/laguna-xs-2.1:free",              # kod, hafif
    "inclusionai/ling-3.0-flash-sante:free",    # hizli
    "nvidia/nemotron-3.5-content-safety:free",  # ozel gorev
    "liquid/lfm-2.5-2.6b:free",                 # cok hafif
    "qwen2.5-coder:3b",                         # YEREL
    "deepseek-r1:1.5b",                         # YEREL
]

sirali, cikanlar = [], []
mevcut = {m.get("model") for m in modeller}

# once siralama listesindekileri ekle (yeni modeller dahil)
for slug in SIRALAMA:
    if slug in mevcut:
        sirali.extend(m for m in modeller if m.get("model") == slug)
    else:
        yeni = next((y for y in YENI if y["model"] == slug), None)
        if yeni:
            sirali.append(yeni)

# kalan modeller (ucretliler) siralama listesinde yok -> sona ekle
for m in modeller:
    if m not in sirali:
        if m.get("model") in CALISMAYAN:
            cikanlar.append(m["model"])
            continue
        sirali.append(m)

print(f"Cikarilan ({len(cikanlar)}):")
for s in cikanlar:
    print("   -", s)

cfg["models"] = sirali
SABLON.write_text(
    json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"\nYeni model sayisi: {len(sirali)}")
for i, m in enumerate(sirali, 1):
    print(f"  {i:2d}. {m['title']}")
