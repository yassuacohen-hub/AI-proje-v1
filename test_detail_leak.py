#!/usr/bin/env python3
"""Detay endpoint sızıntısı: SELECT c.* ile iç alanlar dışarı çıkıyor."""
import requests
import json

# Listedeki ilk firma ID'sini al
list_url = "http://localhost:8000/api/companies?limit=1"
headers = {"Authorization": "Bearer test_key"}

try:
    r = requests.get(list_url, headers=headers, timeout=5)
    r.raise_for_status()
    data = r.json()
    
    if not data.get("items"):
        print("Hata: Firma listesi boş")
        exit(1)
    
    # Detay endpoint'ini test et (company_id yerine doğrudan ID tarat)
    # Çünkü listedeki firma company_id bilgisi yok; sorgu yapması gerekir
    # Alternatif: detay URL'i tahmin et
    detail_url = "http://localhost:8000/api/company/1"  # Varsayılan ID
    
    print(f"Detay endpoint test: {detail_url}")
    r_detail = requests.get(detail_url, headers=headers, timeout=5)
    
    if r_detail.status_code == 200:
        firm = r_detail.json()
        print("\n=== /api/company/{id} yanıtı (TÜYE UYGUN MI?) ===")
        
        leak_fields = {
            "quarantine_reason": "Karantina sebebi (iç alan)",
            "entity_confidence": "Güven puanı (iç alan)",
            "source_record_id": "Ham kayıt ID (iç alan)",
            "description": "Açıklama (dış?)",
            "data_quality_score": "Kalite puanı (dış?)",
            "status_confidence": "Durum güveni (iç?)"
        }
        
        leaks = {}
        for field, desc in leak_fields.items():
            if field in firm and firm[field] is not None:
                leaks[field] = (firm[field], desc)
        
        if leaks:
            print("\n⚠️  SİZINTI BULUNDU:")
            for field, (val, desc) in leaks.items():
                print(f"  {field}: {val}")
                print(f"    → {desc}")
        else:
            print("\n✓ Sızıntı yok")
        
        # Tüm alanları göster
        print("\n=== Tüm dönen alanlar ===")
        for k, v in firm.items():
            if v is not None:
                print(f"  {k}: {v}")
    else:
        print(f"Detay sorgusu başarısız: {r_detail.status_code}")
        print(r_detail.text[:200])
        
except Exception as e:
    print(f"Hata: {e}")
