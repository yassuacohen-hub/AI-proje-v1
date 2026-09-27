#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-218-QUICK-FIX: Telegram Bot with Crash Protection

Wraps infinity_polling() with exception handler to prevent process death.
Auto-reconnects on network/API failures.

Run: python src/company_master/telegram_bot_wrapped.py
"""

import os
import sys
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s",
)
logger = logging.getLogger("TELEGRAM-BOT-WRAPPED")

# Import bot
from telegram_bot import bot, TOKEN

print("\n" + "=" * 80)
print("TELEGRAM BOT — Crash-Protected Polling")
print("=" * 80)
print(f"Token: {TOKEN[:20]}...")
print(f"Status: Polling started with auto-reconnect")
print("=" * 80 + "\n")

def main_with_protection():
    """Bot polling loop with crash protection."""
    retry_count = 0
    max_retries = 10
    backoff_base = 1  # 1 second initial backoff

    while True:
        try:
            logger.info(f"[POLLING] Starting polling loop (attempt {retry_count + 1})")
            bot.infinity_polling(timeout=10, long_polling_timeout=5)

        except KeyboardInterrupt:
            logger.info("[SHUTDOWN] Received SIGINT, stopping gracefully...")
            break

        except Exception as e:
            retry_count += 1
            backoff_seconds = min(backoff_base * (2 ** (retry_count - 1)), 300)  # Cap at 5min

            logger.error(f"[CRASH] Polling failed (attempt {retry_count}/{max_retries}): {e}", exc_info=True)

            if retry_count >= max_retries:
                logger.critical(f"[FATAL] Max retries ({max_retries}) exceeded. Giving up.")
                sys.exit(1)

            logger.warning(f"[RETRY] Reconnecting in {backoff_seconds}s...")
            time.sleep(backoff_seconds)

            # Reset counter on successful polling
            retry_count = 0


if __name__ == "__main__":
    try:
        main_with_protection()
    except KeyboardInterrupt:
        logger.info("[SHUTDOWN] Process stopped by user")
    except Exception as e:
        logger.critical(f"[FATAL] Unhandled exception: {e}", exc_info=True)
        sys.exit(1)
