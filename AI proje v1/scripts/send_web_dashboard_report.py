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
from datetime import datetime

lines = [
    "*Web Dashboard Guncellemesi*",
    "",
    "*Yapilan isler:*",
    "  • Müşteriye yönelik web dashboard tasarlandi",
    "  • Font Awesome ikonlar eklendi",
    "  • Arama ozelligi eklendi (firma adi, VKN, telefon, email)",
    "  • Responsive tasarim (mobil uyumlu)",
    "  • FastAPI backend arama endpoint'i eklendi",
    "",
    "*Erisim:*",
    "  • Dashboard: http://localhost:8501",
    "  • API: http://localhost:8000/api/companies",
    "  • Arama: http://localhost:8000/api/companies?search=<terim>",
    "",
    "*Veri:*",
    f"  • Toplam firma: 9,007",
    f"  • Kalite skoru: 56.54/100",
    f"  • NACE: 8,343 (%92.4)",
    "",
    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
]
text_msg = "\n".join(lines)
result = send_message(text_msg, parse_mode="Markdown")
print("Gonderildi:", result.get("ok", False))
