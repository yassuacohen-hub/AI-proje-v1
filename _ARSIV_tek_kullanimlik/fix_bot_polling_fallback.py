#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bot polling fallback — webhook/polling hybrid mode."""

from pathlib import Path

bot_file = Path("src/company_master/telegram_bot.py")

with open(bot_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# main() fonksiyonunu bul ve değiştir
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if "def main():" in line and "Bot webhook mode" in lines[i+1] if i+1 < len(lines) else False:
        start_idx = i
    if start_idx is not None and "if __name__" in line:
        end_idx = i
        break

if start_idx is not None and end_idx is not None:
    new_main = '''def main():
    """Bot webhook/polling mode — production webhooks, dev polling."""
    import os
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL", "").strip()
    
    if webhook_url:
        logger.info(f"Telegram Bot webhook mode: {webhook_url}")
        logger.info("FastAPI web_app.py:/api/webhooks/telegram endpoint kullanılacak")
    else:
        logger.info("Telegram Bot polling mode (dev/fallback)")
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"Bot polling error: {e}")
            raise


'''
    lines = lines[:start_idx] + [new_main] + lines[end_idx:]
    
    with open(bot_file, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print("[OK] Bot polling fallback mode aktif")
    print("  - TELEGRAM_WEBHOOK_URL set ise: webhook mode")
    print("  - TELEGRAM_WEBHOOK_URL unset: polling mode (dev)")
else:
    print("[ERROR] main() function not found")
