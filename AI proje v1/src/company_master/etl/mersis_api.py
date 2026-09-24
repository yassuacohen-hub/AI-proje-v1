# -*- coding: utf-8 -*-
"""MERSIS / VKN zenginlestirme saglayicilari ve pipeline."""
from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

MERSIS_BASE_URL = os.getenv("MERSIS_BASE_URL", "https://mersis.ticaret.gov.tr")
KYC_SANDBOX_URL = os.getenv("KYC_SANDBOX_URL", "https://api.knowyourcustomer.dev").rstrip("/")
KYC_CLIENT_ID = os.getenv("KYC_CLIENT_ID", "")
KYC_CLIENT_SECRET = os.getenv("KYC_CLIENT_SECRET", "")
CACHE_DIR = Path("data/mersis_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"


def _cache_get(key: str, max_age_seconds: int = 7 * 24 * 3600) -> Optional[Dict]:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        age = time.time() - p.stat().st_mtime
        if age > max_age_seconds:
            return None
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _cache_set(key: str, value: Dict) -> None:
    try:
        _cache_path(key).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


class MERSISProvider:
    name = "mersis"

    def is_available(self) -> bool:
        try:
            r = requests.head(MERSIS_BASE_URL, timeout=10, allow_redirects=True)
            return r.status_code < 500
        except Exception:
            return False

    def search_by_name(self, name: str) -> List[Dict]:
        # MERSIS kamuya acik REST API yok; HTML arayuz uzerinden arama yoktur.
        return []

    def search_by_vkn(self, vkn: str) -> Dict:
        return {}


class KnowYourCustomerProvider:
    name = "knowyourcustomer"

    def __init__(self) -> None:
        self.base_url = KYC_SANDBOX_URL
        self.client_id = KYC_CLIENT_ID
        self.client_secret = KYC_CLIENT_SECRET
        self._token: Optional[str] = None
        self._token_expiry: float = 0.0

    def is_available(self) -> bool:
        if not self.client_id or not self.client_secret:
            return False
        try:
            r = requests.get(f"{self.base_url}/", timeout=10)
            return r.status_code < 500
        except Exception:
            return False

    def _get_token(self) -> Optional[str]:
        now = time.time()
        if self._token and now < self._token_expiry:
            return self._token
        try:
            r = requests.post(
                f"{self.base_url}/connect/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "PublicApi",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=15,
            )
            if r.status_code == 200:
                data = r.json()
                self._token = data.get("access_token")
                # JWT genelde 10 dk gecerlidir; 9 dk'da yenile.
                self._token_expiry = now + 9 * 60
                return self._token
        except Exception as e:
            print(f"KYC token hatasi: {e}")
        return None

    def search_by_name(self, name: str, country: str = "TR") -> List[Dict]:
        token = self._get_token()
        if not token:
            return []
        cache_key = f"kyc_search_name:{country}:{name}"
        cached = _cache_get(cache_key)
        if cached is not None:
            return cached
        try:
            r = requests.get(
                f"{self.base_url}/v2/Companies",
                headers={"Authorization": f"Bearer {token}"},
                params={"name": name, "codeiso31662": country},
                timeout=20,
            )
            if r.status_code == 200:
                data = r.json()
                items = data.get("items", []) or data.get("value", []) or []
                _cache_set(cache_key, items)
                return items
        except Exception as e:
            print(f"KYC arama hatasi: {e}")
        return []

    def search_by_vkn(self, vkn: str, country: str = "TR") -> Dict:
        token = self._get_token()
        if not token:
            return {}
        cache_key = f"kyc_search_vkn:{country}:{vkn}"
        cached = _cache_get(cache_key)
        if cached is not None:
            return cached
        try:
            r = requests.get(
                f"{self.base_url}/v2/Companies",
                headers={"Authorization": f"Bearer {token}"},
                params={"registrationNumber": vkn, "codeiso31662": country},
                timeout=20,
            )
            if r.status_code == 200:
                data = r.json()
                items = data.get("items", []) or data.get("value", []) or []
                result = items[0] if items else {}
                _cache_set(cache_key, result)
                return result
        except Exception as e:
            print(f"KYC VKN arama hatasi: {e}")
        return {}


class TOBBProvider:
    name = "tobb"

    def is_available(self) -> bool:
        return False

    def search_by_name(self, name: str) -> List[Dict]:
        return []

    def search_by_vkn(self, vkn: str) -> Dict:
        return {}


def fetch_company_data(vkn: str, use_cache: bool = True) -> Dict:
    if not vkn or len(vkn) != 10 or not vkn.isdigit():
        return {}
    cache_file = CACHE_DIR / f"{vkn}.json"
    if use_cache and cache_file.exists():
        try:
            age = time.time() - cache_file.stat().st_mtime
            if age < 7 * 24 * 3600:
                return json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    provider = MERSISProvider()
    data = provider.search_by_vkn(vkn)
    if use_cache and data:
        try:
            cache_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
    return data


def sync_mersis_data(limit: int = 100):
    from company_master.db.connection import get_engine
    from sqlalchemy import text

    engine = get_engine()
    synced = 0
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT company_id, tax_number
            FROM companies
            WHERE tax_number IS NOT NULL
              AND tax_number != ''
              AND (mersis_data IS NULL OR mersis_data = '')
            LIMIT :lim
        """), {"lim": limit})
        companies = result.fetchall()

    print(f"MERSIS senkronizasyonu baslatiliyor: {len(companies)} firma")
    for company_id, vkn in companies:
        data = fetch_company_data(vkn)
        if data:
            with engine.begin() as conn:
                conn.execute(text("""
                    UPDATE companies
                    SET mersis_data = :data,
                        mersis_synced_at = :sync_at
                    WHERE company_id = :cid
                """), {
                    "data": json.dumps(data, ensure_ascii=False),
                    "sync_at": datetime.now().isoformat(),
                    "cid": company_id,
                })
                synced += 1
        time.sleep(1)
    print(f"MERSIS senkronizasyonu tamamlandi: {synced}/{len(companies)} firma")


if __name__ == "__main__":
    sync_mersis_data(limit=10)
