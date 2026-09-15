"""Telegram bot bildirim ve long-polling yardimci fonksiyonlari.

Kullanim:
    from src.company_master.utils.telegram_bot import (
        send_message, html_escape, get_updates, parse_command,
        is_authorized, masked_token,
    )

Calisma zamani degiskenleri (.env):
    TELEGRAM_BOT_TOKEN  - Bot token (gizli, .env'de)
    TELEGRAM_CHAT_ID    - Yetkili chat ID'si
    TELEGRAM_BOT_USERNAME - Botun @adicigi isim (komut parsing icin)

NOTE: Environment degiskenleri import aninda degil; her fonksiyon
çaagrisi sirasinda _load_env() ile okunur. Boylece testler monkeypatch
ile env'yi temizleyebilir.
"""
from __future__ import annotations

import html
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TIMEOUT = 30
TELEGRAM_API_BASE = "https://api.telegram.org/bot"


_ALLOWED_TAGS = {"b", "i", "u", "strong", "em", "code", "pre", "a"}


def _load_env() -> None:
    """Calisma zamaninda .env'yi proje kokunden yukler.

    Bos veya ayarlanmamis ortam degiskenlerini .env'deki
    degerlerle doldurur; zaten ayarli degerleri gormez.
    Bu, Docker/bot_service ortamindaki bos TELEGRAM_*
    degerlerinin .env'deki gercek bilgileri kapatmasini engeller.
    """
    for key, value in dotenv_values(ROOT / ".env").items():
        if value and not os.environ.get(key):
            os.environ[key] = value


def _get_token() -> str | None:
    """Calisma zamaninda token'i okur (import aninda onbelleklenmez)."""
    _load_env()
    return os.environ.get("TELEGRAM_BOT_TOKEN")


def _get_chat_id() -> str | None:
    """Calisma zamaninda yetkili chat_id'yi okur."""
    _load_env()
    return os.environ.get("TELEGRAM_CHAT_ID")


def _get_bot_username() -> str | None:
    """Bot username'ini (without @) okur; komut parsing icin."""
    _load_env()
    return os.environ.get("TELEGRAM_BOT_USERNAME")


def masked_token(token: str | None) -> str:
    """Token'i gizler; log/icin guvenli temsil."""
    if not token:
        return "<not set>"
    parts = token.split(":")
    if len(parts) == 2:
        return f"{parts[0]}:****{parts[1][-4:]}"
    return "****"


def html_escape(text: str | None, *, preserve_tags: tuple[str, ...] = ()) -> str:
    """HTML parse_mode icin guvenli escape.

    Mevcut HTML etiketlerini (b, i, u, code, pre, a) korur;
    diger tum ozel karakterleri escape eder.
    """
    if not text:
        return ""
    allowed = set(preserve_tags) | _ALLOWED_TAGS
    pattern = re.compile(
        r"</?(" + "|".join(sorted(allowed)) + r")\b[^>]*>", re.IGNORECASE
    )
    placeholders: dict[str, str] = {}
    counter = 0

    def _placeholder(match: re.Match) -> str:
        nonlocal counter
        tag = match.group(0)
        key = f"__TELEGRAM_TAG_{counter}__"
        placeholders[key] = tag
        counter += 1
        return key

    escaped = pattern.sub(_placeholder, text)
    escaped = html.escape(escaped, quote=True)
    for key, tag in placeholders.items():
        escaped = escaped.replace(key, tag)
    return escaped


def _api_url(endpoint: str) -> str:
    token = _get_token()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set")
    return f"{TELEGRAM_API_BASE}{token}/{endpoint}"


def send_message(
    text: str,
    chat_id: str | None = None,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
) -> dict[str, Any]:
    """Telegram mesaji gonderir.

    her zaman sozluk done:
      {"ok": True/False, "error": "...", "result": {...}}
    """
    token = _get_token()
    if not token:
        return {"ok": False, "error": "TOKEN not set"}
    target = chat_id or _get_chat_id()
    if not target:
        return {"ok": False, "error": "CHAT_ID not set"}

    payload = {
        "chat_id": target,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }
    try:
        resp = requests.post(_api_url("sendMessage"), json=payload, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            return {"ok": False, "error": data.get("description", "unknown error"), "raw": data}
        return {"ok": True, "result": data.get("result", {})}
    except requests.RequestException as exc:
        return {"ok": False, "error": str(exc)}
    except (ValueError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": f"JSON decode: {exc}"}


def get_updates(
    offset: int = 0,
    timeout: int = 30,
    limit: int = 100,
    allowed_updates: list[str] | None = None,
) -> dict[str, Any]:
    """Telegram getUpdates API'sini cagirir (long-polling).

    Returns:
        {"ok": True/False, "error": "...", "result": [...], "next_offset": int}
    """
    token = _get_token()
    if not token:
        return {"ok": False, "error": "TOKEN not set", "result": [], "next_offset": 0}

    params: dict[str, Any] = {
        "offset": offset,
        "timeout": timeout,
        "limit": limit,
    }
    if allowed_updates:
        params["allowed_updates"] = json.dumps(allowed_updates)

    try:
        resp = requests.get(_api_url("getUpdates"), params=params, timeout=timeout + 10)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            return {"ok": False, "error": data.get("description", "unknown error"), "result": [], "next_offset": 0}
        updates = data.get("result", [])
        next_offset = 0
        if updates:
            next_offset = max(u["update_id"] for u in updates) + 1
        return {"ok": True, "result": updates, "next_offset": next_offset}
    except requests.RequestException as exc:
        return {"ok": False, "error": str(exc), "result": [], "next_offset": 0}
    except (ValueError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": f"JSON decode: {exc}", "result": [], "next_offset": 0}


def parse_command(text: str, bot_username: str | None = None) -> dict[str, Any] | None:
    """Telegram mesajini komut + argumanlara ayirir.

    Orn:
        "/start@MyBot merhaba dunya" -> {"command": "start", "bot": "MyBot",
                                         "args": ["merhaba", "dunya"]}
        "/start" -> {"command": "start", "bot": None, "args": []}
        "merhaba" -> None (genuz komut)

    bot_username parametresi verilirse, mesajdaki @BotName kontrolu yapilir;
    farkli botlarin mesajlarini goz ardi eder.
    """
    if not text:
        return None
    text = text.strip()
    if not text.startswith("/"):
        return None

    parts = text.split()
    if not parts:
        return None

    cmd_part = parts[0]
    cmd_match = re.match(r"/([A-Za-z_][A-Za-z0-9_-]*)@?([A-Za-z0-9_-]*)", cmd_part)
    if not cmd_match:
        return None

    command = cmd_match.group(1).lower()
    bot_in_msg = cmd_match.group(2) or None

    # Eger bot_username verildiyse ve mesajda @BotName varsa kontrol et
    if bot_username and bot_in_msg and bot_in_msg.lower() != bot_username.lower():
        return None  # Baska bota ait komut

    args = parts[1:] if len(parts) > 1 else []
    return {
        "command": command,
        "bot": bot_in_msg,
        "args": args,
        "raw": text,
    }


def is_authorized(chat_id: str | int | None, allowed_chat_id: str | None = None) -> bool:
    """Chat ID'yi yetkili chat ID'ye karsilastirir.

    allowed_chat_id verilmezse env'den TELEGRAM_CHAT_ID okunur.
    """
    if chat_id is None:
        return False
    target = allowed_chat_id or _get_chat_id()
    if not target:
        return False
    try:
        return str(chat_id).strip() == str(target).strip()
    except (TypeError, ValueError):
        return False


def send_task_started(task_name: str, agent: str) -> dict[str, Any]:
    """Yeni gorev basladiginda bildirim gonderir."""
    text = (
        "<b>Yeni Gorev Basladi</b>\n"
        f"<b>Ajan:</b> {html_escape(agent)}\n"
        f"<b>Gorev:</b> {html_escape(task_name)}\n"
        f"<i>{time.strftime('%H:%M:%S')}</i>"
    )
    return send_message(text)


def send_task_completed(task_name: str, agent: str, summary: str) -> dict[str, Any]:
    """Gorev tamamlandiginda bildirim gonderir."""
    text = (
        "<b>Gorev Tamamlandi</b>\n"
        f"<b>Ajan:</b> {html_escape(agent)}\n"
        f"<b>Gorev:</b> {html_escape(task_name)}\n"
        f"<b>Ozet:</b> {html_escape(summary[:200])}\n"
        f"<i>{time.strftime('%H:%M:%S')}</i>"
    )
    return send_message(text)


def send_alert(title: str, message: str) -> dict[str, Any]:
    """Uyarı bildirimi gonderir."""
    text = (
        f"<b>{html_escape(title)}</b>\n"
        f"<pre>{html_escape(message[:800])}</pre>\n"
        f"<i>{time.strftime('%H:%M:%S')}</i>"
    )
    return send_message(text)


def send_daily_summary(stats: dict[str, Any]) -> dict[str, Any]:
    """Gunluk ozet raporu gonderir."""
    text = (
        "<b>Gunluk Ozet</b> "
        f"({time.strftime('%Y-%m-%d')})\n\n"
        f"- Toplam firma: <b>{stats.get('total_firms', 0):,}</b>\n"
        f"- Yeni eklenen: <b>{stats.get('new_firms', 0):,}</b>\n"
        f"- Ortalama kalite: <b>{stats.get('avg_quality', 0):.1f}</b>/100\n"
        f"- Aktif gorev: <b>{stats.get('active_tasks', 0)}</b>\n"
        f"- Tamamlanan: <b>{stats.get('completed_tasks', 0)}</b>"
    )
    return send_message(text)


def send_status_report(status: dict[str, Any]) -> dict[str, Any]:
    """Sistem durum raporu gonderir."""
    lines = ["<b>Sistem Durumu</b>\n"]
    for key, value in status.items():
        lines.append(f"{html_escape(str(key))}: {html_escape(str(value))}")
    text = "\n".join(lines) + f"\n\n<i>{time.strftime('%H:%M:%S')}</i>"
    return send_message(text)


if __name__ == "__main__":
    print(f"Token mask: {masked_token(_get_token())}")
    print(f"CHAT_ID: {_get_chat_id()}")
    result = send_message("<b>🤖 Ankara B2B Master Bot</b> aktif. Test mesaji basarili.")
    print(json.dumps(result, ensure_ascii=False, indent=2))
