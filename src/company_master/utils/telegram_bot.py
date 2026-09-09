"""Telegram bot bildirim modulu.

Kullanim:
    from src.company_master.utils.telegram_bot import send_message
    send_message("Merhaba Dunya")

Ortam degiskenleri (.env):
    TELEGRAM_BOT_TOKEN
    TELEGRAM_CHAT_ID
"""
from __future__ import annotations

import os
import json
import time
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
API_URL = f"https://api.telegram.org/bot{TOKEN}" if TOKEN else None
DEFAULT_TIMEOUT = 30


def _masked_token() -> str:
    if not TOKEN:
        return "<not set>"
    parts = TOKEN.split(":")
    if len(parts) == 2:
        return f"{parts[0]}:****{parts[1][-4:]}"
    return "****"


def send_message(text: str, chat_id: Optional[str] = None, parse_mode: str = "HTML", disable_web_page_preview: bool = True) -> dict:
    if not TOKEN:
        print("[TELEGRAM UYARI] TOKEN ayarlanmamis.")
        return {"ok": False, "error": "TOKEN not set"}
    if not chat_id and not CHAT_ID:
        print("[TELEGRAM UYARI] CHAT_ID ayarlanmamis.")
        return {"ok": False, "error": "CHAT_ID not set"}

    target = chat_id or CHAT_ID
    payload = {
        "chat_id": target,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }
    try:
        resp = requests.post(f"{API_URL}/sendMessage", json=payload, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            print(f"[TELEGRAM HATA] {data}")
        else:
            try:
                print(f"[TELEGRAM OK] chat_id={target}: {text[:60]}...")
            except UnicodeEncodeError:
                print("[TELEGRAM OK] Mesaj gonderildi")
        return data
    except requests.RequestException as exc:
        print(f"[TELEGRAM HATA] Istek basarisiz: {exc}")
        return {"ok": False, "error": str(exc)}


def send_task_started(task_name: str, agent: str) -> dict:
    text = f"🚀 <b>Yeni Gorev Basladi</b>\n<b>Ajan:</b> {agent}\n<b>Gorev:</b> {task_name}\n<i>{time.strftime('%H:%M:%S')}</i>"
    return send_message(text)


def send_task_completed(task_name: str, agent: str, summary: str) -> dict:
    text = f"✅ <b>Gorev Tamamlandi</b>\n<b>Ajan:</b> {agent}\n<b>Gorev:</b> {task_name}\n<b>Ozet:</b> {summary[:200]}\n<i>{time.strftime('%H:%M:%S')}</i>"
    return send_message(text)


def send_alert(title: str, message: str) -> dict:
    text = f"⚠️ <b>{title}</b>\n<pre>{message[:800]}</pre>\n<i>{time.strftime('%H:%M:%S')}</i>"
    return send_message(text)


def send_daily_summary(stats: dict) -> dict:
    text = (
        f"📊 <b>Gunluk Ozet</b> ({time.strftime('%Y-%m-%d')})\n\n"
        f"• Toplam firma: <b>{stats.get('total_firms', 0):,}</b>\n"
        f"• Yeni eklenen: <b>{stats.get('new_firms', 0):,}</b>\n"
        f"• Ortalama kalite: <b>{stats.get('avg_quality', 0):.1f}</b>/100\n"
        f"• Aktif gorev: <b>{stats.get('active_tasks', 0)}</b>\n"
        f"• Tamamlanan: <b>{stats.get('completed_tasks', 0)}</b>"
    )
    return send_message(text)


if __name__ == "__main__":
    print(f"Token mask: {_masked_token()}")
    print(f"CHAT_ID: {CHAT_ID}")
    result = send_message("<b>🤖 Ankara B2B Master Bot</b> aktif. Test mesaji basarili.")
    print(json.dumps(result, ensure_ascii=False, indent=2))
