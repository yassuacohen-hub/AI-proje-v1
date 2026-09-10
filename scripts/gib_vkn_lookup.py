#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GIB VKN lookup prototipi.

Y11 (GIB VKN dogrulama entegrasyonu) icin hazirlanan prototip.
Resmi GIB vkn.gov.tr servisine yonelik kesif ve entegrasyon hazirligi.

Kullanim:
    python scripts/gib_vkn_lookup.py --vkn 1234567890
    python scripts/gib_vkn_lookup.py --name "Firma Unvani" --limit 10
    python scripts/gib_vkn_lookup.py --batch data/vkn_batch_input.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

try:
    import requests
    from sqlalchemy import text
    from company_master.db.connection import get_engine
except ImportError as e:
    print(f"Bagimlilik hatasi: {e}")
    sys.exit(1)

GIB_BASE_URL = os.getenv("GIB_BASE_URL", "https://vkn.gov.tr").rstrip("/")
UA = "AnkaraB2B-Bot/1.0 (+research contact: site owner)"
CACHE_DIR = ROOT / "data" / "gib_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(key: str) -> Path:
    h = hashlib.sha256(key.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{h}.json"


def _cache_get(key: str, max_age: int = 7 * 24 * 3600) -> Optional[Dict]:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        age = time.time() - p.stat().st_mtime
        if age > max_age:
            return None
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _cache_set(key: str, value: Dict) -> None:
    try:
        _cache_path(key).write_text(
            json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


class GIBProvider:
    name = "gib"

    def __init__(self, base_url: str = GIB_BASE_URL) -> None:
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UA, "Accept-Language": "tr"})

    def is_available(self) -> bool:
        try:
            r = self.session.head(self.base_url, timeout=10, allow_redirects=True)
            return r.status_code < 500
        except Exception:
            return False

    def _request(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        cache_key = f"gib:{path}:{json.dumps(params, sort_keys=True)}"
        cached = _cache_get(cache_key)
        if cached is not None:
            return cached
        try:
            r = self.session.get(
                f"{self.base_url}{path}",
                params=params,
                timeout=15,
                allow_redirects=True,
            )
            result: Dict[str, Any] = {"status": r.status_code}
            if r.status_code == 200:
                try:
                    result["data"] = r.json()
                except ValueError:
                    result["text"] = r.text[:2000]
            else:
                result["error"] = r.text[:500]
            _cache_set(cache_key, result)
            return result
        except Exception as e:
            return {"status": 0, "error": str(e)}

    def search_by_vkn(self, vkn: str) -> Dict[str, Any]:
        if not vkn or len(vkn) != 10 or not vkn.isdigit():
            return {"status": 400, "error": "Gecersiz VKN formati"}
        return self._request("/api/v1/vkn", {"vkn": vkn})

    def search_by_name(self, name: str) -> Dict[str, Any]:
        if not name or len(name.strip()) < 3:
            return {"status": 400, "error": "Gecersiz firma unvani"}
        return self._request("/api/v1/search", {"name": name.strip()})


def cmd_lookup_vkn(vkn: str, provider: GIBProvider) -> None:
    result = provider.search_by_vkn(vkn)
    print(f"VKN: {vkn}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_lookup_name(name: str, limit: int, provider: GIBProvider) -> None:
    result = provider.search_by_name(name)
    print(f"Unvan: {name}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_batch(path: str, provider: GIBProvider) -> None:
    p = Path(path)
    if not p.exists():
        print(f"Dosya bulunamadi: {path}")
        return
    records = [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
    print(f"Batch islem: {len(records)} kayit")
    found = 0
    for i, rec in enumerate(records):
        vkn = rec.get("vkn") or rec.get("vergi_no") or rec.get("tax_number")
        name = rec.get("unvan") or rec.get("legal_name") or rec.get("name")
        if vkn:
            result = provider.search_by_vkn(str(vkn))
            if result.get("status") == 200 and result.get("data"):
                found += 1
                print(f"[{i}] VKN {vkn} -> DOGRULANDI")
            else:
                print(f"[{i}] VKN {vkn} -> bulunamadi/gecersiz")
        elif name:
            result = provider.search_by_name(str(name))
            if result.get("status") == 200 and result.get("data"):
                found += 1
                print(f"[{i}] Unvan {name[:40]} -> sonuc var")
            else:
                print(f"[{i}] Unvan {name[:40]} -> bulunamadi")
        else:
            print(f"[{i}] Atlaniyor: VKN/unvan eksik")
        time.sleep(1)
    print(f"Toplam: {len(records)} islendi, {found} sonuclandi")


def cmd_health(provider: GIBProvider) -> None:
    status = "erisilebilir" if provider.is_available() else "erisilemez"
    print(f"GIB servis durumu: {status}")
    print(f"Base URL: {provider.base_url}")


def main() -> None:
    ap = argparse.ArgumentParser(description="GIB VKN lookup prototipi")
    ap.add_argument("--vkn", help="10 haneli VKN ile dogrulama")
    ap.add_argument("--name", help="Firma unvani ile arama")
    ap.add_argument("--limit", type=int, default=10, help="Arama sonuc limiti")
    ap.add_argument("--batch", help="JSONL batch dosyasi")
    ap.add_argument("--health", action="store_true", help="Servis durumu kontrolu")
    args = ap.parse_args()

    provider = GIBProvider()
    if args.health:
        cmd_health(provider)
    elif args.vkn:
        cmd_lookup_vkn(args.vkn, provider)
    elif args.name:
        cmd_lookup_name(args.name, args.limit, provider)
    elif args.batch:
        cmd_batch(args.batch, provider)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
