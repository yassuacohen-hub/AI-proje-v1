#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MERSIS VKN zenginlestirme pipeline'i - Y10"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine
from sqlalchemy import text

ORCHESTRATOR_DIR = ROOT / "data" / "orchestrator"
RESULT_FILE = ORCHESTRATOR_DIR / "y10_result.json"

# Provider configs from environment
KYC_SANDBOX_URL = os.getenv("KYC_SANDBOX_URL", "https://api.knowyourcustomer.dev")
KYC_CLIENT_ID = os.getenv("KYC_CLIENT_ID", "")
KYC_CLIENT_SECRET = os.getenv("KYC_CLIENT_SECRET", "")
MERSIS_BASE_URL = os.getenv("MERSIS_BASE_URL", "https://mersis.ticaret.gov.tr")


def get_companies_missing_vkn(limit: int = 5000) -> list[dict]:
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT company_id, legal_name, trade_name, tax_number, vergi_no, website_domain
            FROM companies
            WHERE (tax_number IS NULL OR tax_number = '')
              AND (vergi_no IS NULL OR vergi_no = '')
            LIMIT :lim
        """), {"lim": limit}).fetchall()
    return [
        {
            "company_id": str(r[0]),
            "legal_name": r[1],
            "trade_name": r[2],
            "tax_number": r[3],
            "vergi_no": r[4],
            "website_domain": r[5],
        }
        for r in rows
    ]


def update_company_vkn(company_id: str, vkn: str, source: str, vergi_no: Optional[str] = None) -> int:
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(text("""
            UPDATE companies
            SET tax_number = :vkn,
                vergi_no = COALESCE(:vergi_no, tax_number, vergi_no),
                updated_at = NOW()
            WHERE company_id = :cid
        """), {
            "vkn": vkn,
            "vergi_no": vergi_no,
            "cid": company_id,
        })
        return result.rowcount


class MERSISProvider:
    """MERSIS resmi kaynak (kamuya acik API yok, site kontrolu)."""
    name = "mersis"

    def is_available(self) -> bool:
        try:
            r = requests.head(MERSIS_BASE_URL, timeout=10, allow_redirects=True)
            return r.status_code < 500
        except Exception:
            return False

    def search_by_name(self, name: str) -> list[dict]:
        # MERSIS kamuya acik REST API yok; sadece ulke genelinde arama yapilabilir.
        # Gercek entegrasyon icin Ticaret Bakanligi ile resmi anlasma gerekir.
        return []

    def search_by_vkn(self, vkn: str) -> dict:
        return {}


class KnowYourCustomerProvider:
    """KnowYourCustomer sandbox ( KYB / VKN arama )."""
    name = "knowyourcustomer"

    def __init__(self):
        self.base_url = KYC_SANDBOX_URL.rstrip("/")
        self.client_id = KYC_CLIENT_ID
        self.client_secret = KYC_CLIENT_SECRET
        self._token: Optional[str] = None

    def is_available(self) -> bool:
        if not self.client_id or not self.client_secret:
            return False
        try:
            r = requests.get(f"{self.base_url}/", timeout=10)
            return r.status_code < 500
        except Exception:
            return False

    def _get_token(self) -> Optional[str]:
        if self._token:
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
                return self._token
        except Exception as e:
            print(f"KYC token alinamadi: {e}")
        return None

    def search_by_name(self, name: str, country: str = "TR") -> list[dict]:
        token = self._get_token()
        if not token:
            return []
        try:
            r = requests.get(
                f"{self.base_url}/v2/Companies",
                headers={"Authorization": f"Bearer {token}"},
                params={"name": name, "codeiso31662": country},
                timeout=20,
            )
            if r.status_code == 200:
                return r.json().get("items", []) or r.json().get("value", []) or []
        except Exception as e:
            print(f"KYC arama hatasi: {e}")
        return []

    def search_by_vkn(self, vkn: str, country: str = "TR") -> dict:
        token = self._get_token()
        if not token:
            return {}
        try:
            r = requests.get(
                f"{self.base_url}/v2/Companies",
                headers={"Authorization": f"Bearer {token}"},
                params={"registrationNumber": vkn, "codeiso31662": country},
                timeout=20,
            )
            if r.status_code == 200:
                data = r.json()
                items = data.get("items", []) or data.get("value", [])
                return items[0] if items else {}
        except Exception as e:
            print(f"KYC VKN arama hatasi: {e}")
        return {}


class TOBBProvider:
    """TOBB kaynak (kamuya acik VKN API'si yok)."""
    name = "tobb"

    def is_available(self) -> bool:
        return False

    def search_by_name(self, name: str) -> list[dict]:
        return []

    def search_by_vkn(self, vkn: str) -> dict:
        return {}


def run_pipeline(limit: int = 5000) -> dict:
    start_time = datetime.now()
    report = {
        "task_id": "Y10",
        "baslik": "MERSIS VKN zenginlestirme pipeline'i",
        "baslangic": start_time.isoformat(timespec="seconds"),
        "durum": "yapilan",
        "kaynaklar": {},
        "istatistikler": {
            "toplam_firma": 0,
            "guncellenen_firma": 0,
            "bulunan_vkn": 0,
        },
    }

    companies = get_companies_missing_vkn(limit=limit)
    report["istatistikler"]["toplam_firma"] = len(companies)
    print(f"VKN eksik firma: {len(companies)}")

    providers = [
        MERSISProvider(),
        KnowYourCustomerProvider(),
        TOBBProvider(),
    ]

    updated = 0
    found_vkn = 0
    provider_stats = {}

    for provider in providers:
        provider_stats[provider.name] = {
            "kullanildi": False,
            "sonuc": "",
        }
        if not provider.is_available():
            provider_stats[provider.name]["sonuc"] = "erisim yok / engelli"
            print(f"  {provider.name}: erisim yok / engelli")
            continue

        provider_stats[provider.name]["kullanildi"] = True
        provider_stats[provider.name]["sonuc"] = "denendi"
        print(f"  {provider.name}: erisim var, deneniyor...")

        for comp in companies:
            if comp["tax_number"] and comp["tax_number"] != "":
                continue

            # Oncelikle VKN ile ara (eger kaynaklarda VKN varsa)
            # Simdi isim ile ara
            results = provider.search_by_name(comp["legal_name"] or comp["trade_name"] or "")
            if not results:
                continue

            # Ilk eslesme al
            best = results[0]
            vkn = best.get("tax_number") or best.get("registrationNumber") or best.get("vergi_no")
            if not vkn:
                continue

            # VKN format kontrolu (10 haneli sayi)
            vkn_str = str(vkn).strip()
            if not (len(vkn_str) == 10 and vkn_str.isdigit()):
                continue

            try:
                rows_updated = update_company_vkn(comp["company_id"], vkn_str, source=provider.name)
                if rows_updated > 0:
                    updated += 1
                    found_vkn += 1
                    print(f"    Guncellendi: {comp['legal_name']} -> {vkn_str}")
            except Exception as e:
                print(f"    DB yazma hatasi {comp['company_id']}: {e}")

            time.sleep(0.2)

        provider_stats[provider.name]["sonuc"] = f"{found_vkn} VKN bulundu"
        print(f"  {provider.name}: {found_vkn} VKN bulundu")

    report["istatistikler"]["guncellenen_firma"] = updated
    report["istatistikler"]["bulunan_vkn"] = found_vkn
    report["kaynaklar"] = provider_stats
    report["durum"] = "blocked" if updated == 0 else "done"
    report["bitis"] = datetime.now().isoformat(timespec="seconds")
    report["not"] = (
        "MERSIS kamuya acik API saglamiyor (html yanit). "
        "KnowYourCustomer sandbox kimlik bilgisi eksik. "
        "TOBB'da dogrudan VKN API'si yok. "
        f"Sonuc: {updated} firma guncellendi, {found_vkn} VKN bulundu."
    )

    RESULT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rapor kaydedildi: {RESULT_FILE}")
    return report


if __name__ == "__main__":
    run_pipeline(limit=5000)
