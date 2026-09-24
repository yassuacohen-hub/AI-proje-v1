#!/usr/bin/env python3
"""API SELECT c.* sızıntısı test."""
import requests
import json

url = "http://localhost:8000/api/company/1"
headers = {"Authorization": "Bearer test_key"}

try:
    r = requests.get(url, headers=headers, timeout=5)
    r.raise_for_status()
    data = r.json()
    
    print("=== /api/company/1 yanıtı ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # İç alanlar kontrol et
    leak_fields = ["quarantine_reason", "entity_confidence", "source_record_id", "description", "data_quality_score"]
    leaks = {k: v for k, v in data.items() if k in leak_fields and v is not None}
    
    if leaks:
        print("\n⚠️ SİZINTI: İç alanlar dışarı çıkıyor:")
        for k, v in leaks.items():
            print(f"  - {k}: {v}")
    else:
        print("\n✓ Sızıntı yok (iç alanlar filtered)")
        
except Exception as e:
    print(f"Hata: {e}")
