#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bot webhook fix — polling disable + debug_catch_all disable."""

import re
from pathlib import Path

bot_file = Path("src/company_master/telegram_bot.py")

with open(bot_file, "r", encoding="utf-8") as f:
    content = f.read()

# FIX 1: debug_catch_all handler'ı disable et
pattern1 = r'@bot\.message_handler\(func=lambda message: True\)\s+def debug_catch_all\(message\):.*?(?=\n\n# =====)'
replacement1 = '# DISABLED: debug_catch_all handler tüm mesajları yakalaması bot\'u donduruyor'
content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)

# FIX 2: polling -> webhook mode
old_main = """def main():
    \"\"\"Bot başlat.\"\"\"
    logger.info("Starting Telegram Bot polling...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise"""

new_main = """def main():
    \"\"\"Bot webhook mode'da çalıştır (FastAPI üzerinden process_new_updates).\"\"\"
    logger.info("Telegram Bot webhook mode aktif")
    logger.info("Polling DISABLED — FastAPI web_app.py:/api/webhooks/telegram endpoint kullan")"""

content = content.replace(old_main, new_main)

with open(bot_file, "w", encoding="utf-8") as f:
    f.write(content)

print("[OK] Bot webhook mode'a geçirildi:")
print("  - debug_catch_all handler disabled")
print("  - polling mode -> webhook mode")
