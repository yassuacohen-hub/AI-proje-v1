#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

sys.path.insert(0, str(ROOT / "src"))

from company_master.utils.telegram_bot import send_message

# Test mesajı
result = send_message("🟢 <b>Dashboard aktif</b>\nhttp://localhost:8501")
print("Sonuc:", result.get("ok", False))
if not result.get("ok"):
    print("Hata:", result.get("error"))
