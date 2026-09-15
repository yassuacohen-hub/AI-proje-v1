# -*- coding: utf-8 -*-
"""Telegram bot arka plan servisi — canonical polling wrapper.

Bu modul python-telegram-bot kutuphanesini KULLANMAZ.
Canonical long-polling motoru scripts/telegram_polling.py'dir.

Kullanim:
    # Servis olarak baslat (arakplan process):
    python -m company_master.telegram.bot_service

    # Direkt polling baslat:
    python src/company_master/telegram/bot_service.py --foreground
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.company_master.utils.telegram_bot import send_message, masked_token

load_dotenv(ROOT / ".env")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _script_path() -> str:
    """Canonical polling script'inin tam yolunu dondurur."""
    return str(ROOT / "scripts" / "telegram_polling.py")


def start_polling(token: Optional[str] = None, foreground: bool = False) -> "subprocess.Popen | None":
    """Canonical polling script'ini baslatir.

    Args:
        token: token (env'den okunur eger None)
        foreground: Eger True ise bloklayarak calistir (blocking).
          False (varsayilan): arka planda subprocess olarak baslat.
    """
    import subprocess

    real_token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not real_token:
        logger.error("TELEGRAM_BOT_TOKEN bulunamadi!")
        return None

    env = os.environ.copy()
    env["TELEGRAM_BOT_TOKEN"] = real_token
    if os.environ.get("TELEGRAM_CHAT_ID"):
        env["TELEGRAM_CHAT_ID"] = os.environ["TELEGRAM_CHAT_ID"]
    bot_user = os.environ.get("TELEGRAM_BOT_USERNAME")
    if bot_user:
        env["TELEGRAM_BOT_USERNAME"] = bot_user

    script = _script_path()
    logger.info("Canonical polling baslatiliyor: %s", script)

    try:
        if foreground:
            proc = subprocess.run(
                [sys.executable, script],
                env=env,
                cwd=str(ROOT),
            )
            return None
        else:
            proc = subprocess.Popen(
                [sys.executable, script],
                env=env,
                cwd=str(ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return proc
    except Exception as exc:
        logger.error("Polling baslatilamadi: %s", exc)
        raise


def send_test_message() -> dict:
    """Test mesaji gonderir."""
    return send_message("<b>🤖 Bot servisi aktif.</b>")


def main() -> None:
    """Bot servisini baslatir."""
    import argparse

    parser = argparse.ArgumentParser(description="Telegram bot servis yoneticisi")
    parser.add_argument("--foreground", action="store_true",
                        help="Bloklayarak calistir (debug icin)")
    args = parser.parse_args()

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN bulunamadi!")
        sys.exit(1)

    logger.info("Telegram bot servisi baslatiliyor (token: %s)...", masked_token(token)[:15])
    start_polling(token=token, foreground=args.foreground)
    logger.info("Telegram bot servisi calistirildi.")


if __name__ == "__main__":
    main()
