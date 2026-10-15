#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Huginn Data Insights - TOBB API Integration Test
Tests Company Card 02 (Basic Info) and Card 04 (Gazette PDF) endpoints.

Run: python test_tobb_integration.py
"""

import asyncio
import json
import os
import sys
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime

import httpx
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

load_dotenv()


# ================================================================
# CONFIGURATION
# ================================================================
TOBB_API_URL = os.getenv("TOBB_API_URL", "https://tobb.org.tr")
TOBB_API_KEY = os.getenv("TOBB_API_KEY")
TOBB_API_SECRET = os.getenv("TOBB_API_SECRET")
TOBB_CARD_02_COST_TL = float(os.getenv("TOBB_CARD_02_COST_TL", "19.49"))
TOBB_CARD_04_COST_TL = float(os.getenv("TOBB_CARD_04_COST_TL", "48.73"))

# Test VKN/TCKN - Replace with real test values
TEST_VKN = os.getenv("TEST_VKN", "1234567890")  # 10-digit VKN for companies
TEST_TCKN = os.getenv("TEST_TCKN", "12345678901")  # 11-digit TCKN for individuals
TEST_MERSIS = os.getenv("TEST_MERSIS", "0123456789012345")  # 16-digit MERSIS


# ================================================================
# PYDANTIC MODELS (Matching TOBB Response Schemas)
# ================================================================
class TobbCompanyCard02Response(BaseModel):
    """TOBB Şirket Kartı 02 - Temel Firma Bilgileri"""
    Basarili: bool
    HataKodu: Optional[str] = None
    HataMesaji: Optional[str] = None
    Veri: Optional[Dict[str, Any]] = None
    
    @validator("Veri", pre=True)
    def parse_veri(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return {}
        return v or {}


class TobbCompanyCard04Response(BaseModel):
    """TOBB Şirket Kartı 04 - Resmi Gazete Teşhirleri (Base64 PDF)"""
    Basarili: bool
    HataKodu: Optional[str] = None
    HataMesaji: Optional[str] = None
    Veri: Optional[str] = None  # Base64 encoded PDF


class TobbBalanceResponse(BaseModel):
    """TOBB Bakiye Sorgulama"""
    Basarili: bool
    HataKodu: Optional[str] = None
    HataMesaji: Optional[str] = None
    Veri: Optional[Dict[str, Any]] = None


@dataclass
class TestResult:
    test_name: str
    passed: bool
    details: str
    duration_ms: int
    response_data: Optional[Dict] = None


# ================================================================
# TOBB CLIENT
# ================================================================
class TobbTestClient:
    def __init__(self, base_url: str, api_key: str, api_secret: str):
        # base_url is for Card 02/03 (webservis13). Card 04 needs webservis15
        self.base_url_card02 = base_url.rstrip("/")
        # Derive Card 04 endpoint from base_url pattern - fix double date bug
        if "webservis13_20260911" in self.base_url_card02:
            self.base_url_card04 = self.base_url_card02.replace("webservis13_20260911", "webservis15_20260911")
        elif "webservis13" in self.base_url_card02:
            self.base_url_card04 = self.base_url_card02.replace("webservis13", "webservis15_20260911")
        elif "webservis12_20260911" in self.base_url_card02:
            self.base_url_card04 = self.base_url_card02.replace("webservis12_20260911", "webservis15_20260911")
        elif "webservis12" in self.base_url_card02:
            self.base_url_card04 = self.base_url_card02.replace("webservis12", "webservis15_20260911")
        else:
            # Default fallback
            self.base_url_card04 = "https://ttsg.tobb.org.tr/webservis15_20260911.php"
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)
        self.results: list[TestResult] = []
    
    async def close(self):
        await self.client.aclose()
    
    def _build_payload(self, metod: str, **params) -> dict:
        """Build standard TOBB request payload"""
        return {
            "Metod": metod,
            "Kodu": self.api_key,
            "Sifre": self.api_secret,
            **params
        }
    
    async def _post(self, payload: dict, use_card04: bool = False) -> dict:
        """Send POST request to TOBB API. Card 04 uses different endpoint (webservis15)."""
        target_url = self.base_url_card04 if use_card04 else self.base_url_card02
        try:
            response = await self.client.post(
                target_url,
                json=payload,
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"Basarili": False, "HataKodu": str(e.response.status_code), "HataMesaji": e.response.text}
        except Exception as e:
            return {"Basarili": False, "HataKodu": "EXCEPTION", "HataMesaji": str(e)}
    
    def _record_result(self, name: str, passed: bool, details: str, duration_ms: int, data: Optional[Dict] = None):
        self.results.append(TestResult(name, passed, details, duration_ms, data))
        status = "[OK]" if passed else "[FAIL]"
        print(f"  {status} {name} ({duration_ms}ms) - {details}")
    
    # ------------------------------------------------------------
    # TEST METHODS
    # ------------------------------------------------------------
    async def test_balance(self) -> bool:
        """Test 1: Bakiye Sorgulama"""
        start = datetime.now()
        payload = self._build_payload("BakiyeSorgula")
        response = await self._post(payload)
        duration = int((datetime.now() - start).total_seconds() * 1000)
        
        try:
            parsed = TobbBalanceResponse(**response)
            passed = parsed.Basarili
            if passed and parsed.Veri:
                balance = parsed.Veri.get("Bakiye", "N/A")
                details = f"Bakiye: {balance} TL, Min Gerekli: {TOBB_CARD_02_COST_TL} TL"
            else:
                details = f"Hata: {parsed.HataKodu} - {parsed.HataMesaji}"
        except Exception as e:
            passed = False
            details = f"Parse hatası: {e}"
        
        self._record_result("TOBB Bakiye Sorgulama", passed, details, duration, response)
        return passed
    
    async def test_card_02_vkn(self) -> bool:
        """Test 2: Şirket Kartı 02 - VKN ile sorgulama"""
        start = datetime.now()
        payload = self._build_payload("SirketKarti02", VergiNo=TEST_VKN)
        response = await self._post(payload)
        duration = int((datetime.now() - start).total_seconds() * 1000)
        
        try:
            parsed = TobbCompanyCard02Response(**response)
            passed = parsed.Basarili
            if passed and parsed.Veri:
                veri = parsed.Veri
                unvan = veri.get("Unvan", "N/A")
                durum = veri.get("Durum", "N/A")
                nace = veri.get("NaceKodu", "N/A")
                details = f"Ünvan: {unvan[:50]}, Durum: {durum}, NACE: {nace}"
            else:
                details = f"Hata: {parsed.HataKodu} - {parsed.HataMesaji}"
        except Exception as e:
            passed = False
            details = f"Parse hatası: {e}"
        
        self._record_result("TOBB Şirket Kartı 02 (VKN)", passed, details, duration, response)
        return passed
    
    async def test_card_02_mersis(self) -> bool:
        """Test 3: Şirket Kartı 02 - MERSIS ile sorgulama"""
        start = datetime.now()
        payload = self._build_payload("SirketKarti02", MersisNo=TEST_MERSIS)
        response = await self._post(payload)
        duration = int((datetime.now() - start).total_seconds() * 1000)
        
        try:
            parsed = TobbCompanyCard02Response(**response)
            passed = parsed.Basarili
            if passed and parsed.Veri:
                veri = parsed.Veri
                unvan = veri.get("Unvan", "N/A")
                details = f"Ünvan: {unvan[:50]}"
            else:
                details = f"Hata: {parsed.HataKodu} - {parsed.HataMesaji}"
        except Exception as e:
            passed = False
            details = f"Parse hatası: {e}"
        
        self._record_result("TOBB Şirket Kartı 02 (MERSIS)", passed, details, duration, response)
        return passed
    
    async def test_card_04_vkn(self) -> bool:
        """Test 4: Şirket Kartı 04 - Resmi Gazete PDF (VKN)"""
        start = datetime.now()
        payload = self._build_payload("SirketKarti04", VergiNo=TEST_VKN)
        response = await self._post(payload, use_card04=True)
        duration = int((datetime.now() - start).total_seconds() * 1000)
        
        try:
            parsed = TobbCompanyCard04Response(**response)
            passed = parsed.Basarili
            if passed and parsed.Veri:
                # Base64 PDF validation
                import base64
                try:
                    pdf_bytes = base64.b64decode(parsed.Veri)
                    is_pdf = pdf_bytes[:4] == b"%PDF"
                    size_kb = len(pdf_bytes) / 1024
                    details = f"PDF geçerli: {is_pdf}, Boyut: {size_kb:.1f} KB"
                    passed = passed and is_pdf
                except Exception as e:
                    details = f"Base64 decode hatası: {e}"
                    passed = False
            else:
                details = f"Hata: {parsed.HataKodu} - {parsed.HataMesaji}"
        except Exception as e:
            passed = False
            details = f"Parse hatası: {e}"
        
        self._record_result("TOBB Şirket Kartı 04 (VKN - PDF)", passed, details, duration, response)
        return passed
    
    async def test_card_04_mersis(self) -> bool:
        """Test 5: Şirket Kartı 04 - Resmi Gazete PDF (MERSIS)"""
        start = datetime.now()
        payload = self._build_payload("SirketKarti04", MersisNo=TEST_MERSIS)
        response = await self._post(payload, use_card04=True)
        duration = int((datetime.now() - start).total_seconds() * 1000)
        
        try:
            parsed = TobbCompanyCard04Response(**response)
            passed = parsed.Basarili
            if passed and parsed.Veri:
                import base64
                try:
                    pdf_bytes = base64.b64decode(parsed.Veri)
                    is_pdf = pdf_bytes[:4] == b"%PDF"
                    size_kb = len(pdf_bytes) / 1024
                    details = f"PDF geçerli: {is_pdf}, Boyut: {size_kb:.1f} KB"
                    passed = passed and is_pdf
                except Exception as e:
                    details = f"Base64 decode hatası: {e}"
                    passed = False
            else:
                details = f"Hata: {parsed.HataKodu} - {parsed.HataMesaji}"
        except Exception as e:
            passed = False
            details = f"Parse hatası: {e}"
        
        self._record_result("TOBB Şirket Kartı 04 (MERSIS - PDF)", passed, details, duration, response)
        return passed
    
    async def test_invalid_vkn(self) -> bool:
        """Test 6: Geçersiz VKN - Hata yönetimi testi"""
        start = datetime.now()
        payload = self._build_payload("SirketKarti02", VergiNo="0000000000")
        response = await self._post(payload)
        duration = int((datetime.now() - start).total_seconds() * 1000)
        
        try:
            parsed = TobbCompanyCard02Response(**response)
            # Invalid VKN should return Basarili: false with error code
            passed = not parsed.Basarili
            details = f"Beklenen hata alındı: {parsed.HataKodu} - {parsed.HataMesaji}"
        except Exception as e:
            passed = False
            details = f"Parse hatası: {e}"
        
        self._record_result("TOBB Geçersiz VKN Hata Yönetimi", passed, details, duration, response)
        return passed
    
    async def test_missing_credentials(self) -> bool:
        """Test 7: Eksik kimlik bilgisi - Güvenlik testi"""
        start = datetime.now()
        payload = {"Metod": "SirketKarti02", "VergiNo": TEST_VKN}  # Kodu/Sifre yok
        response = await self._post(payload)
        duration = int((datetime.now() - start).total_seconds() * 1000)
        
        try:
            parsed = TobbCompanyCard02Response(**response)
            passed = not parsed.Basarili
            details = f"Kimlik hatası beklendi: {parsed.HataKodu}"
        except Exception as e:
            passed = False
            details = f"Parse hatası: {e}"
        
        self._record_result("TOBB Eksik Kimlik Bilgisi", passed, details, duration, response)
        return passed
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("\n" + "="*60)
        print("HUGINN DATA INSIGHTS - TOBB API ENTEGRASYON TESTİ")
        print("="*60)
        print(f"API Endpoint: {TOBB_API_URL}")
        print(f"API Key: {'SET' if TOBB_API_KEY else 'NOT SET'}")
        print(f"Test VKN: {TEST_VKN}")
        print(f"Test MERSIS: {TEST_MERSIS}")
        print(f"Card 02 Cost: {TOBB_CARD_02_COST_TL} TL")
        print(f"Card 04 Cost: {TOBB_CARD_04_COST_TL} TL")
        print("="*60 + "\n")
        
        tests = [
            ("Bakiye Sorgulama", self.test_balance),
            ("Şirket Kartı 02 (VKN)", self.test_card_02_vkn),
            ("Şirket Kartı 02 (MERSIS)", self.test_card_02_mersis),
            ("Şirket Kartı 04 PDF (VKN)", self.test_card_04_vkn),
            ("Şirket Kartı 04 PDF (MERSIS)", self.test_card_04_mersis),
            ("Geçersiz VKN Hata Yönetimi", self.test_invalid_vkn),
            ("Eksik Kimlik Bilgisi", self.test_missing_credentials),
        ]
        
        for name, test_func in tests:
            print(f"\n[>] {name}")
            try:
                await test_func()
            except Exception as e:
                self._record_result(name, False, f"Test exception: {e}", 0)
        
        self.print_summary()
    
    def print_summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*60)
        print("TEST OZETI")
        print("="*60)
        print(f"Toplam Test: {total}")
        print(f"Basarili:    {passed} [OK]")
        print(f"Basarisiz:   {failed} [FAIL]")
        print(f"Basari Orani: %{pass_rate:.1f}")
        print("="*60)
        
        if failed > 0:
            print("\nBASARISIZ TESTLER:")
            for r in self.results:
                if not r.passed:
                    print(f"  [FAIL] {r.test_name}: {r.details}")
        
        # Save detailed results
        output = {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "api_url": TOBB_API_URL,
                "api_key": TOBB_API_KEY[:4] + "****",
                "test_vkn": TEST_VKN,
                "test_mersis": TEST_MERSIS,
            },
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": pass_rate
            },
            "results": [asdict(r) for r in self.results]
        }
        
        with open("tobb_test_results.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\nDetaylı sonuçlar kaydedildi: tobb_test_results.json")
        
        return failed == 0


# ================================================================
# MAIN
# ================================================================
async def main():
    print("TOBB API Entegrasyon Testi Başlatılıyor...")
    print(f"API Endpoint: {TOBB_API_URL}")
    print(f"API Key: {'SET' if TOBB_API_KEY else 'NOT SET'}")
    print(f"Test VKN: {TEST_VKN}")
    
    # Validate credentials are provided
    if not TOBB_API_KEY or not TOBB_API_SECRET:
        print("\n[UYARI] TOBB_API_KEY ve TOBB_API_SECRET ortam değişkenleri ayarlanmamış!")
        print("   Gerçek test için .env dosyasında TOBB_API_KEY ve TOBB_API_SECRET ayarlayın.")
        print("   Ön ödemeli bakiye en az 50.000 TL olmalıdır.\n")
    
    client = TobbTestClient(TOBB_API_URL, TOBB_API_KEY, TOBB_API_SECRET)
    
    try:
        success = await client.run_all_tests()
        return 0 if success else 1
    finally:
        await client.close()


if __name__ == "__main__":
    # Windows event loop policy fix
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)