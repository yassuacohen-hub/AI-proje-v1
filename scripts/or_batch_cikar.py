# -*- coding: utf-8 -*-
import json
from pathlib import Path

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = Path(__file__).resolve().parents[1]
SABLON = KOK / "docs" / "continue_config.json"
cfg = json.loads(SABLON.read_text(encoding="utf-8-sig"))

once = len(cfg["models"])
# :batch modelleri ayri Batch API gerektirir; Continue /chat/completions
# kullanir ve "No endpoints found" 404 doner -> listeden cikarilir.
cfg["models"] = [m for m in cfg["models"] if ":batch" not in m.get("model", "")]
SABLON.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n",
                  encoding="utf-8")
print(f"Once: {once} -> Sonra: {len(cfg['models'])}")

# NVIDIA dogrudan modeli bir ara OK verdi, simdi HATA. Kisa not ekle.
notlar = cfg.setdefault("_not", [])
notlar.insert(13, "BATCH MODELLER (2026-10-01): ':batch' slug'lari %50-75 indirimli "
                 "ama AYRI Batch API ister. Continue /chat/completions kullandigi icin "
                 "'No endpoints found' 404 doner -> listeden CIKARILDI. Indirimli "
                 "fiyat icin /api/v1/batch endpoint'i + SDK gerekir.")
print("Not eklendi.")
