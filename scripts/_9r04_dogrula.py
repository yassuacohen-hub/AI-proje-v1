# -*- coding: utf-8 -*-
"""9R-04 canlı doğrulama: lokal + tünel uçlarında health, web model listesi ve
yeni web_fetch/web_search imzasının davranışı.

Amaç: yapılandırma (Dashboard → Providers) olmadan ulaşılabilen bilgiyi toplar:
  1. Health (local + tunnel)
  2. /v1/models/web listesi (kurulu web provider'ları)
  3. web_fetch(provider="ollama", max_characters=2000) — çalışan tek provider
  4. web_search(provider="tavily") — henüz eklenmediyse anlamlı hata vermeli
"""
from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pathlib  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.company_master.gateway.ninerouter_client import (  # noqa: E402
    NineRouter,
    get_client,
)

UCLAR = {
    "LOKAL": "http://localhost:20128",
    "TUNEL": "https://r3qmzpf.abc-tunnel.us",
}


def _baslik(t: str) -> None:
    print(f"\n=== {t} ===")


def main() -> int:
    aktif = get_client().base_url
    print(f"Aktif NINEROUTER_URL (env): {aktif}")

    for etiket, base in UCLAR.items():
        _baslik(f"{etiket} ({base})")
        nr = NineRouter(base_url=base, max_retries=0)
        try:
            print(f"health={nr.health()}")
        except Exception as exc:  # noqa: BLE001
            print(f"health HATA: {type(exc).__name__}: {exc}")
            continue

        try:
            modeller = nr.list_models("web")
            print(f"web model sayısı={len(modeller)}")
            for m in modeller:
                print(f"  - {m.get('id')} | kind={m.get('kind')} | owned_by={m.get('owned_by')}")
        except Exception as exc:  # noqa: BLE001
            print(f"list_models(web) HATA: {type(exc).__name__}: {exc}")

        # Yeni imza (skill dokümanı): suffix'siz provider + format + max_characters
        # Firecrawl — JS render'lı kariyer sayfaları için asıl hedef.
        print("-- web_fetch(provider='firecrawl', max_characters=2000) --")
        try:
            sonuc = nr.web_fetch(
                "https://9router.com",
                provider="firecrawl",
                max_characters=2000,
            )
            ic = sonuc.get("content")
            print(
                f"web_fetch(firecrawl) OK type={type(ic).__name__} "
                f"len={len(ic) if isinstance(ic, str) else ic} "
                f"ilk200={str(ic)[:200] if ic else ''!r}"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"web_fetch(firecrawl) HATA: {type(exc).__name__}: {_kisa(exc)}")

        # Tavily Extract — web_fetch'in ikincil sağlayıcısı (bulk extract/raw_content)
        print("-- web_fetch(provider='tavily', max_characters=2000) --")
        try:
            sonuc = nr.web_fetch(
                "https://9router.com",
                provider="tavily",
                max_characters=2000,
            )
            ic = sonuc.get("content")
            print(
                f"web_fetch(tavily) OK type={type(ic).__name__} "
                f"len={len(ic) if isinstance(ic, str) else ic} "
                f"ilk200={str(ic)[:200] if ic else ''!r}"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"web_fetch(tavily) HATA: {type(exc).__name__}: {_kisa(exc)}")

        print("-- web_search(provider='tavily') --")
        try:
            sonuc = nr.web_search(
                "9Router open source", provider="tavily", max_results=3
            )
            if isinstance(sonuc, dict) and sonuc.get("results"):
                ilk = sonuc["results"][0]
                print(
                    f"web_search OK sonuç={len(sonuc['results'])} "
                    f"ilk_url={ilk.get('url')} ilk_baslik={ilk.get('title')!r}"
                )
            else:
                print(f"web_search dict döndü ama sonuç yok: {str(sonuc)[:300]}")
        except Exception as exc:  # noqa: BLE001
            print(f"web_search(tavily) HATA: {type(exc).__name__}: {_kisa(exc)}")

    return 0


def _kisa(exc: Exception) -> str:
    s = str(exc)
    if len(s) > 350:
        return s[:350] + "..."
    return s


if __name__ == "__main__":
    raise SystemExit(main())