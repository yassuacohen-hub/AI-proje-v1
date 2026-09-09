# -*- coding: utf-8 -*-
"""Telegram bot arka plan servisi.

Kullanım:
    export TELEGRAM_BOT_TOKEN="your_bot_token_here"
    python -m company_master.telegram.bot_service
"""

import os
import time
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    """Bot başlangıç komutu."""
    keyboard = [
        [InlineKeyboardButton("📊 Durum Raporu", callback_data="report_status")],
        [InlineKeyboardButton("📈 Kalite Skorları", callback_data="report_quality")],
        [InlineKeyboardButton("📋 Yardım", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "🚀 *Huginn Company Intelligence Bot*\nAnkara B2B Intelligence Platformu\n\nLütfen bir işlem seçin:",
        reply_markup=reply_markup, parse_mode="Markdown"
    )


def button_handler(update: Update, context: CallbackContext):
    """Buton tıklama işlemleri."""
    query = update.callback_query
    query.answer()
    if query.data == "report_status":
        report_status(query)
    elif query.data == "report_quality":
        report_quality(query)
    elif query.data == "help":
        query.edit_message_text(
            "📖 *Yardım Menüsü*\n\nKomutlar:\n/start - Ana menü\n/status - Sistem durumu\n/quality - Kalite raporu"
        )


def report_status(update):
    """Sistem durumunu raporla."""
    from company_master.db.connection import get_engine
    from sqlalchemy import text
    engine = get_engine()
    try:
        with engine.connect() as conn:
            total = conn.execute(text("SELECT COUNT(*) FROM companies WHERE is_ankara=TRUE")).fetchone()[0]
            avg_score = conn.execute(text("SELECT AVG(data_quality_score) FROM companies WHERE is_ankara=TRUE")).fetchone()[0]
        msg = f"📊 *Sistem Durumu*\n\n📋 Toplam: {total:,}\n📈 Ort. Kalite: {avg_score:.1f}/100\n🕒 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Status hata: {e}")
        update.message.reply_text("❌ Rapor alınamadı.")


def report_quality(update):
    """Kalite skoru raporu."""
    from company_master.db.connection import get_engine
    from sqlalchemy import text
    engine = get_engine()
    try:
        with engine.connect() as conn:
            buckets = conn.execute(text("""
                SELECT CASE WHEN data_quality_score>=80 THEN '80-100' WHEN data_quality_score>=60 THEN '60-79'
                WHEN data_quality_score>=40 THEN '40-59' ELSE '0-39' END as bucket, COUNT(*) as cnt
                FROM companies WHERE is_ankara=TRUE GROUP BY 1 ORDER BY 1 DESC
            """)).fetchall()
        msg = "📈 *Kalite Dağılımı*\n\n"
        for row in buckets:
            msg += f"{row.bucket}: {row.cnt:,}\n"
        update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Quality hata: {e}")
        update.message.reply_text("❌ Rapor alınamadı.")


def main():
    """Bot'u başlat."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN bulunamadı!")
        return
    updater = Updater(token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("status", lambda u, c: report_status(u)))
    dp.add_handler(CommandHandler("quality", lambda u, c: report_quality(u)))
    dp.add_handler(CallbackQueryHandler(button_handler))
    updater.start_polling()
    logger.info("Telegram bot başlatıldı.")
    try:
        while True: time.sleep(10)
    except KeyboardInterrupt:
        updater.stop()


if __name__ == "__main__":
    main()