#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test Telegram bot with Unicode-safe logging."""
import sys
sys.path.insert(0, "src")
from company_master.utils.telegram_bot import send_message

# Test with simple ASCII message first
result = send_message("<b>Test</b> mesaji")
print("Sonuc:", result.get("ok", False))

# Test with Unicode message
result2 = send_message("📊 <b>Rapor</b>\nTest mesaji")
print("Sonuc2:", result2.get("ok", False))
