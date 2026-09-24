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
    "🔄 <b>Multi-OSB Merger Tamamlandi</b>",
    "",
    "📊 <b>Ozet:</b>",
    "  • Kaynak: OSTIM (5485) + ASO (785)",
    "  • Birlestirilen firma: 5756",
    "  • VKN gruplari: 26",
    "  • İsim gruplari: 5730",
    "",
    "📌 <b>Veri doluluk oranları (merged):</b>",
    "  • Adres: 5752 (99.9%)",
    "  • NACE: 5756 (100.0%)",
    "  • Web: 5038 (87.5%)",
    "  • E-posta: 2407 (41.8%)",
    "  • VKN: 716 (12.4%)",
    "  • Telefon: 685 (11.9%)",
    "",
    "✅ <b>Sonraki adim:</b>",
    "  • Merged veriyi DB'ye yazmak",
    "  • İvedik/Başkent scraper'larini tamamlamak",
    "",
    f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
]
text_msg = "\n".join(lines)
result = send_message(text_msg)
print("Gonderildi:", result.get("ok", False))
