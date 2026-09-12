#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9R-04 geçici keşif scripti: 9Router web provider modellerini listeler.

- NINEROUTER_URL .env'den okunur (ayrıca lokal + tünel uçları zorlanır).
- /v1/models/web çıktısındaki model adları (suffiksli/suffiksiz) teyit edilir.
- Gizli değer yazdırılmaz; yalnız URL ve model/status bilgisi basılır.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Windows konsolunda Türkçe/UTF-8 çıktı için
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.company_master.gateway.ninerouter_client import NineRouter  # noqa: E402


def _deneme(url: str, label: str) -> None:
    print(f"\n=== {label} -> {url} ===")
    nr = NineRouter(base_url=url, max_retries=1)
    try:
        models = nr.list_models(kind="web")
        print(f"health: {nr.health()}")
        print(f"web model sayisi: {len(models) if isinstance(models, list) else 'dict'}")
        for m in models[:40] if isinstance(models, list) else []:
            ad = m.get("id") or m.get("name") or m.get("model") or m
            print(f"  - {ad}")
    except Exception as exc:  # noqa: BLE001
        print(f"HATA: {exc}")


def main() -> int:
    # .env'den gelen aktif URL (gizli değer maskelenmez, URL zaten genel)
    import os

    aktif = os.environ.get("NINEROUTER_URL", "")
    print(f"Aktif NINEROUTER_URL (env): {aktif or '(yok — varsayılan localhost)'}")

    # Lokal uç
    _deneme("http://localhost:20128", "LOKAL")

    # Tünel uç (9R-02e'de canlı doğrulanan adres)
    _deneme("https://r3qmzpf.abc-tunnel.us", "TUNEL")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())