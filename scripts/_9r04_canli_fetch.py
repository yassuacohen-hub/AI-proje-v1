#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9R-04 geçici canlı test: web_fetch provider adı + alan adı doğrulama.

Bulgular:
- list_models("web") = ['ollama/fetch']  (suffiksli ID)
- `/v1/web/fetch` "ollama/fetch" için 400 Unknown provider döndü.
Beklenti (skill): provider adı suffiksiz kullanılır ("ollama", "firecrawl"...).
Ayrıca alan adı: kod `outputFormat` kullanıyor; skill `format` diyor.

Bu script her iki kombinasyonu lokal + tünel uçlarında dener ve yalnız
sonuç özeti (uzunluk / ilk karakterler) basar; gizli değer yazdırmaz.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.company_master.gateway.ninerouter_client import NineRouter  # noqa: E402

HEDEF_URL = "https://9router.com"


def _dene(url: str, label: str, provider: str, output_format: str | None = None,
          extra: dict | None = None) -> None:
    print(f"\n=== {label} | provider={provider} ===")
    nr = NineRouter(base_url=url, max_retries=0)
    try:
        sonuc = nr.web_fetch(HEDEF_URL, provider=provider,
                             output_format=output_format or "markdown",
                             extra=extra)
        content = sonuc.get("content")
        if isinstance(content, str):
            print(f"ok type=markdown len={len(content)} ilk200={content[:200]!r}")
        else:
            print(f"ok dict keys={list(sonuc.keys())}")
            print(str(sonuc)[:400])
    except Exception as exc:  # noqa: BLE001
        print(f"HATA ({type(exc).__name__}): {exc}")


def main() -> int:
    for base, label in (("http://localhost:20128", "LOKAL"),
                        ("https://r3qmzpf.abc-tunnel.us", "TUNEL")):
        # A) suffiksiz provider + mevcut outputFormat alanı
        _dene(base, f"{label} A(ollama/outputFormat)", provider="ollama")
        # B) suffiksiz provider + skill format alanı (extra ile)
        _dene(base, f"{label} B(ollama/format)", provider="ollama",
              extra={"format": "markdown", "max_characters": 2000})
        # C) suffiksiz provider + outputFormat + max_characters
        _dene(base, f"{label} C(ollama/both)", provider="ollama",
              extra={"format": "markdown", "max_characters": 2000})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())