# -*- coding: utf-8 -*-
"""Codex profil portföyü: tek kelimelik güç adlarıyla ~/.codex/<ad>.config.toml.

Tüm seçimler 2026-10-20 /responses canlı testiyle doğrulandı (15/16 OK).
Parola/anahtar EKRANA BASILMAZ (D-380).
"""
import tomllib
from pathlib import Path

HOME = Path.home() / ".codex"

PROFILLER = {
    # ad: (aciklama, saglayici, model)
    "guclu":     ("GÜÇLÜ · ChatGPT Pro hesabı · en iyi kod/zeka · 4sn", "9router", "cx/gpt-5.6-luna"),
    "kod":       ("KOD · ChatGPT Pro yedek hesap · döner paylaşımlı · 4sn", "9router", "cx/gpt-5.6-terra"),
    "claude":    ("CLAUDE · Claude Pro combo (tam uyum) · 24sn", "9router", "fullclaude"),
    "bedava":    ("BEDAVA · hızlı işler için · Nvidia Nemotron · 8sn", "9router",
                  "openrouter/nvidia/nemotron-3.5-lightning:free"),
    "derin":     ("DERİN · akıl yürüten bedava model · 7sn", "9router",
                  "openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"),
    "oto":       ("OTOMATİK · bedava yönlendirici kendisi seçer · 5sn", "9router", "bzl/auto:free"),
    "evren":     ("EVREN · bedava T.C. API · hızlı + güçlü kod · 3sn", "evren", "deepseek-v4.1-flash"),
    "evrenderin": ("EVREN DERİN · GLM ağır ama sağlam düşünme · 62sn", "evren", "glm-5.3"),
    "hizli":     ("HIZLI · en ucuz hızlı sohbet · Evren Qwen · 3sn", "evren", "qwen3.8-flash-next"),
}

MENU = """# Codex Model Portföyü (2026-10-20, hepsi CANLI test edildi)

Secim: `codex -p <ad>` (CLI) veya masaüstünde profile karşılığı.
Güç kelimesi = ne işe iyi. Sure = PONG testi ölçümü.

| Profil | Güç kelimesi | Model | Kaynak | Ücret | Sn |
|---|---|---|---|---|---|
| guclu | GÜÇLÜ | cx/gpt-5.6-luna | ChatGPT Pro | pro-hesap | 3.8 |
| kod | KOD | cx/gpt-5.6-terra | ChatGPT Pro (2. hesap) | pro-hesap | 4.0 |
| claude | CLAUDE | fullclaude combo | Claude Pro | pro-hesap | 23.9 |
| bedava | HIZLI-BEDAVA | nemotron-3.5-lightning:free | 9Router | BEDAVA | 8.0 |
| derin | DERİN | nemotron-3-nano-omni...reasoning:free | 9Router | BEDAVA | 6.9 |
| oto | OTOMATİK | bzl/auto:free | 9Router | BEDAVA | 5.2 |
| evren | GÜÇLÜ-BEDAVA | deepseek-v4.1-flash | Evren | BEDAVA | 2.6 |
| evrenderin | DERİN-YAVAŞ | glm-5.3 | Evren | BEDAVA | 62.2 |
| hizli | EN-HIZLI | qwen3.8-flash-next | Evren | BEDAVA | 3.3 |

Dusen adaylar (canli testte 503 — listeye ALINMADI): laguna, glm-5.2, gemma-4 (9R),
kr/* Kilo kanali, cc/* tekli (yalniz fullclaude combo calisir).
"""


def main():
    # 1) config.toml BOM temizliği (tomllib okuyabilsin; codex de temiz dosya görsün)
    cfg = HOME / "config.toml"
    ham = cfg.read_bytes()
    if ham.startswith(b"\xef\xbb\xbf"):
        cfg.write_bytes(ham[3:])
        print("BOM temizlendi")
    with open(cfg, "rb") as f:
        ana = tomllib.load(f)
    print("config.toml PARSE OK · providerlar:", list(ana["model_providers"]))

    # 2) profilleri yaz ve doğrula
    for ad, (aciklama, sag, model) in PROFILLER.items():
        yol = HOME / f"{ad}.config.toml"
        icerik = (f'# GÜÇ: {aciklama}\n'
                  f'# Kullanım: codex -p {ad}\n'
                  f'model_provider = "{sag}"\n'
                  f'model = "{model}"\n'
                  f'model_reasoning_effort = "medium"\n')
        yol.write_text(icerik, encoding="utf-8")
        with open(yol, "rb") as f:
            tomllib.load(f)
        print(f"PROFIL OK: {ad:<12} -> {sag}/{model}")

    # 3) insan menüsü
    (HOME / "MODELLER.md").write_text(MENU, encoding="utf-8")
    print("MENU: ~/.codex/MODELLER.md")

    # 4) panel parola dosyası deseni var mı (DEĞER BASDAN)
    gizli = Path(r"C:\Huginn Data Projesi\Huginn Data Insights\secrets.vds_9router.md")
    if gizli.exists():
        metin = gizli.read_text(encoding="utf-8", errors="replace")
        print("secrets dosyasi VAR · 'Panel' deseni:",
              ("Panel sifresi" in metin) or ("Panel şifresi" in metin),
              "· backtick satir sayisi:", metin.count("`") // 2)
    else:
        print("secrets.vds_9router.md YOK")


if __name__ == "__main__":
    main()
