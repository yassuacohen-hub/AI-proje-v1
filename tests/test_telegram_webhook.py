#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-216: Telegram Webhook Integration Tests

Test Protocol: D-216_CALLBACK_ROUTING_TEST.md
- 6 curl examples covering main menu flows
- Webhook endpoint: POST /api/webhooks/telegram
- Health check: GET /api/webhooks/telegram/health
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Webhook test configuration
WEBHOOK_URL = "http://localhost:8000/api/webhooks/telegram"
HEALTH_URL = "http://localhost:8000/api/webhooks/telegram/health"

# Test data: (name, callback_data, expected_response_contains)
TEST_CASES = [
    (
        "TEST 1: Ana Menu -> Pano Menusu",
        "menu:pano",
        ["ok", "message"],
    ),
    (
        "TEST 2: Pano -> Tamamlanan Gorevler",
        "pano:done",
        ["ok", "message"],
    ),
    (
        "TEST 3: Chat -> Broadcast Input",
        "chat:broadcast",
        ["ok", "message"],
    ),
    (
        "TEST 4: Tetikler -> Utku's Tetikler",
        "tetikler:utku",
        ["ok", "message"],
    ),
    (
        "TEST 5: Rapor -> KPI Detayi",
        "rapor_detail:kpi",
        ["ok", "message"],
    ),
    (
        "TEST 6: Ayarlar -> Baglanti Kontrol",
        "ayarlar:baglanti",
        ["ok", "message"],
    ),
]


def build_telegram_update(callback_data: str) -> Dict[str, Any]:
    """Telegram callback_query update yapisi olustur."""
    return {
        "update_id": 123456789,
        "callback_query": {
            "id": "callback_query_id",
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
                "language_code": "tr",
            },
            "chat_instance": "1234567890",
            "data": callback_data,
            "message": {
                "message_id": 1,
                "date": int(datetime.now().timestamp()),
                "chat": {
                    "id": 123456789,
                    "type": "private",
                    "first_name": "Test",
                    "username": "testuser",
                },
            },
        },
    }


def run_health_check() -> bool:
    """Telegram webhook health check endpoint'ini test et."""
    print("\n" + "=" * 80)
    print("HEALTH CHECK")
    print("=" * 80)
    
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "GET", HEALTH_URL],
            capture_output=True,
            text=True,
            timeout=5,
        )
        
        if result.returncode != 0:
            print("[FAIL] Health check endpoint unreachable")
            print("   Error: {}".format(result.stderr))
            return False
        
        data = json.loads(result.stdout)
        print("[PASS] Health check response")
        print("   Status: {}".format(data.get('status', 'unknown')))
        print("   Bot Token Configured: {}".format(data.get('bot_token_configured', False)))
        print("   Polling Mode: {}".format(data.get('polling_mode', False)))
        
        return True
    
    except json.JSONDecodeError:
        print("[FAIL] Invalid JSON response")
        print("   Response: {}".format(result.stdout))
        return False
    
    except subprocess.TimeoutExpired:
        print("[FAIL] Request timeout (>5s)")
        return False
    
    except Exception as e:
        print("[FAIL] {}".format(e))
        return False


def run_webhook_test(test_name: str, callback_data: str, expected_fields: list) -> bool:
    """Webhook endpoint'ini test et."""
    print("\n{}".format(test_name))
    print("-" * 80)
    
    # Telegram update nesnesi olustur
    payload = build_telegram_update(callback_data)
    
    # curl komutu
    curl_cmd = [
        "curl",
        "-s",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),
        WEBHOOK_URL,
    ]
    
    print("Callback Data: {}".format(callback_data))
    print("Endpoint: POST {}".format(WEBHOOK_URL))
    
    try:
        result = subprocess.run(
            curl_cmd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        
        if result.returncode != 0:
            print("[FAIL] Request failed")
            print("   Error: {}".format(result.stderr))
            return False
        
        # Response JSON parse
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError:
            print("[FAIL] Invalid JSON response")
            print("   Response: {}".format(result.stdout))
            return False
        
        # Beklenen alanlari kontrol et
        missing_fields = []
        for field in expected_fields:
            if field not in response:
                missing_fields.append(field)
        
        if missing_fields:
            print("[FAIL] Missing fields in response: {}".format(missing_fields))
            print("   Response: {}".format(json.dumps(response, indent=2)))
            return False
        
        # Basarili
        if response.get("ok") is True:
            print("[PASS] Update processed successfully")
            print("   Update ID: {}".format(response.get('update_id')))
            print("   Message: {}".format(response.get('message')))
        else:
            print("[WARN] Response ok != true")
            print("   Response: {}".format(json.dumps(response, indent=2)))
        
        return True
    
    except subprocess.TimeoutExpired:
        print("[FAIL] Request timeout (>5s)")
        return False
    
    except Exception as e:
        print("[FAIL] {}".format(e))
        return False


def main() -> int:
    """Tum webhook testlerini calistir."""
    print("\n" + "=" * 80)
    print("D-216: TELEGRAM WEBHOOK INTEGRATION TEST SUITE")
    print("=" * 80)
    print("Time: {}".format(datetime.now().isoformat()))
    print("Webhook URL: {}".format(WEBHOOK_URL))
    
    # Health check
    if not run_health_check():
        print("\n[WARN] Health check failed. Endpoint may not be running.")
        print("   Make sure web_app.py is running: python web_app.py")
        return 1
    
    # Webhook tests
    print("\n" + "=" * 80)
    print("WEBHOOK TESTS")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, callback_data, expected_fields in TEST_CASES:
        if run_webhook_test(test_name, callback_data, expected_fields):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("Total Tests: {}".format(len(TEST_CASES)))
    print("Passed: {} [OK]".format(passed))
    print("Failed: {} [FAIL]".format(failed))
    
    if failed == 0:
        print("\n[OK] All tests passed!")
        return 0
    else:
        print("\n[FAIL] {} test(s) failed".format(failed))
        return 1


if __name__ == "__main__":
    sys.exit(main())
