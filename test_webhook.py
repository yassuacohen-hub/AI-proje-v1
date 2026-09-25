#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bot webhook test — Telegram webhook set."""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(".env")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

if not TELEGRAM_BOT_TOKEN:
    print("[ERROR] TELEGRAM_BOT_TOKEN not set")
    exit(1)

webhook_url = "http://localhost:8000/api/webhooks/telegram"
api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"

payload = {
    "url": webhook_url,
    "allowed_updates": ["message", "callback_query"]
}

try:
    resp = requests.post(api_url, json=payload, timeout=10)
    result = resp.json()
    
    if result.get("ok"):
        print(f"[OK] Webhook set: {webhook_url}")
        print(f"[OK] Allowed updates: {payload['allowed_updates']}")
    else:
        print(f"[ERROR] Webhook set failed: {result.get('description')}")
except Exception as e:
    print(f"[ERROR] Connection error: {e}")
    print("Note: localhost:8000 unreachable — running on dev machine?")
