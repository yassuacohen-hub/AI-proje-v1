#!/usr/bin/env python3
"""API /api/companies listesi test."""
import requests
import json

url = "http://localhost:8000/api/companies"
headers = {"Authorization": "Bearer test_key"}
params = {"limit": 1}

try:
    r = requests.get(url, headers=headers, params=params, timeout=5)
    print(f"Status: {r.status_code}")
    if r.status_code == 401:
        print("Auth gerekli. Token gereken mi? Kontrol et.")
    elif r.status_code == 500:
        print("Server error. Logs kontrol et.")
        print(r.text[:500])
    else:
        data = r.json()
        print("=== /api/companies yanıtı (1 firma) ===")
        if isinstance(data, list) and len(data) > 0:
            print(json.dumps(data[0], indent=2, ensure_ascii=False))
        elif isinstance(data, dict):
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(data)
            
except Exception as e:
    print(f"Hata: {e}")
