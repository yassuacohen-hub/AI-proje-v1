# -*- coding: utf-8 -*-
"""DENEY: Codex GUI model listesi bayat models_cache.json'dan geliyorsa,
cache'e kendi modellerimizi ekleyince GUI'de gorunur mu?

Geri alinabilir: once yedek alinir (models_cache.json.yedek-<zaman>).
Sema bilimi: mevcut GORUNUR bir oge (visibility != hide) kalip olarak kopyalanir,
yalniz slug/display_name/description degistirilir.
"""
import json
import shutil
import time
import urllib.request
from pathlib import Path

K9 = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
CACHE = Path.home() / ".codex" / "models_cache.json"

# GUI'de gorunur olmak isteyen portfoy: (slug, gorunen ad, aciklama)
PORTFOY = [
    ("gpt-5.6-luna", "1-GUCU · ChatGPT Pro en guclu", "En guclu kod ve akil yurutme (ChatGPT Pro hesabi)"),
    ("gpt-5.6-terra", "2-KOD · ChatGPT Pro yedek hesap", "Kod yazimi; diger hesap yorulunca bu devreye girer"),
    ("fullclaude", "3-CLAUDE · Claude Pro", "Claude Pro hesabi (uzun dosya + duzenleme ustasi)"),
    ("openrouter/nvidia/nemotron-3.5-lightning:free", "4-BEDAVA-HIZLI · ucretsiz", "Ucretsiz, hizli gunluk isler"),
    ("openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free", "5-DERIN · ucretsiz dusunen", "Ucretsiz, adim adim dusunen model"),
    ("bzl/auto:free", "6-OTO · kendisi secer", "Ucretsiz, isi en uygun ucretsiz modele dagitir"),
    ("deepseek-v4.1-flash", "7-EVREN-GUCLU · ucretsiz", "Evren (TR) ucretsiz API; kod + ajan, cok hizli"),
    ("glm-5.3", "8-EVREN-DERIN · ucretsiz agir", "Evren ucretsiz; en derin dusunme ama yavas"),
    ("qwen3.8-flash-next", "9-EN-HIZLI · ucretsiz", "Evren ucretsiz; en ucuz ve en hizli sohbet"),
]


def gorunur_kalip(modeller):
    for m in modeller:
        if m.get("visibility") != "hide":
            return m
    return modeller[0]


def main():
    yedek = CACHE.with_name(f"models_cache.yedek-{time.strftime('%Y%m%d_%H%M%S')}.json")
    shutil.copy2(CACHE, yedek)
    print("YEDEK:", yedek.name)

    d = json.loads(CACHE.read_text(encoding="utf-8"))
    mevcut = {m.get("slug") for m in d["models"]}
    kalip = gorunur_kalip(d["models"])
    print("kalip slug:", kalip.get("slug"), "| alan sayisi:", len(kalip))

    eklenen = 0
    for slug, ad, acik in PORTFOY:
        if slug in mevcut:
            # mevcut ogeyi yalniz yeniden adlandir (GUI'de guc kelimesi gorunsun)
            for m in d["models"]:
                if m.get("slug") == slug:
                    m["display_name"] = ad
                    m["description"] = acik
                    m["visibility"] = "list"
                    eklenen += 1
            continue
        y = json.loads(json.dumps(kalip))
        y["slug"] = slug
        y["display_name"] = ad
        y["description"] = acik
        y["visibility"] = "list"
        y["supported_in_api"] = True
        d["models"].append(y)
        eklenen += 1

    d["fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%S.000000000Z", time.gmtime())
    d.pop("etag", None)
    CACHE.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    gorunur = [m["slug"] for m in d["models"] if m.get("visibility") != "hide"]
    print(f"GUNCELLENDI: {eklenen} kayit · toplam model {len(d['models'])} · GUI listesi {len(gorunur)}")
    for s in gorunur:
        print("  -", s)


if __name__ == "__main__":
    main()
