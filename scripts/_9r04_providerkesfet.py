# -*- coding: utf-8 -*-
"""9R-04 ek keşif: firecrawl/tavily anahtarları neden görünmüyor?

- /v1/models/info?id=<id> per-model metadata
- /v1/models/web ham listesi (kind + çıktısı)
- Olası durum uçları: /api/health, /api/providers, /api/keys (varsa)
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import requests  # noqa: E402

from src.company_master.gateway.ninerouter_client import NineRouter  # noqa: E402

UCLAR = {
    "LOKAL": "http://localhost:20128",
    "TUNEL": "https://r3qmzpf.abc-tunnel.us",
}


def _hucre(etiket: str, base: str) -> None:
    print(f"\n=== {etiket} ({base}) ===")
    nr = NineRouter(base_url=base, max_retries=0)
    api_key = nr.api_key or ""
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    # 1) Ham /v1/models/web
    try:
        r = requests.get(f"{base}/v1/models/web", headers=headers, timeout=15)
        print(f"GET /v1/models/web -> {r.status_code}")
        try:
            j = r.json()
            data = j.get("data", j) if isinstance(j, dict) else j
            print(json.dumps(data, ensure_ascii=False)[:1500])
        except ValueError:
            print(r.text[:500])
    except Exception as exc:  # noqa: BLE001
        print(f"models/web HATA: {type(exc).__name__}: {exc}")

    # 2) Per-model info
    for mid in ("tavily/search", "firecrawl/fetch", "ollama/fetch"):
        try:
            r = requests.get(
                f"{base}/v1/models/info", params={"id": mid}, headers=headers, timeout=15
            )
            print(f"--- models/info id={mid} -> {r.status_code}")
            try:
                print(json.dumps(r.json(), ensure_ascii=False)[:800])
            except ValueError:
                print(r.text[:300])
        except Exception as exc:  # noqa: BLE001
            print(f"models/info {mid} HATA: {type(exc).__name__}: {exc}")

    # 3) Olası durum uçları (404 kabul edilebilir — keşif amaçlı)
    for path in ("/api/providers", "/api/keys", "/api/config", "/v1/providers"):
        try:
            r = requests.get(f"{base}{path}", headers=headers, timeout=10)
            snippet = r.text[:200].replace("\n", " ")
            print(f"GET {path} -> {r.status_code}: {snippet}")
        except Exception as exc:  # noqa: BLE001
            print(f"GET {path} HATA: {type(exc).__name__}: {exc}")


def main() -> int:
    for etiket, base in UCLAR.items():
        _hucre(etiket, base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())