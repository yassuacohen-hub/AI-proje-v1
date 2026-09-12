# -*- coding: utf-8 -*-
"""Telegram bot — periodik durum bildirimi.

Belirli araliklarla sistem durumu / gunluk ozetini Telegram'a gonderir.

Calisma zamani degiskenleri (.env):
    TELEGRAM_BOT_TOKEN
    TELEGRAM_CHAT_ID
    TELEGRAM_PERIODIC_INTERVAL_SECONDS (varsayilan: 3600)
    TELEGRAM_PERIODIC_ENABLED (varsayilan: 1)

Kullanim:
    python scripts/telegram_periodic.py             # sonsuz dongu
    python scripts/telegram_periodic.py --once       # tek sefer
    python scripts/telegram_periodic.py --interval 600
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys
import time
import traceback
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT))

from src.company_master.utils.telegram_bot import (
    _get_chat_id,
    _get_token,
    _load_env,
    html_escape,
    send_message,
)

DEFAULT_INTERVAL = 3600


def _load_polling_module():
    """scripts/telegram_polling.py'yi dinamik olarak yukler."""
    spec = importlib.util.spec_from_file_location(
        "telegram_polling", SCRIPT_DIR / "telegram_polling.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError("telegram_polling.py yuklenemedi")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_periodic_message() -> str:
    """Periodik olarak gonderilecek mesaji olusturur."""
    try:
        polling = _load_polling_module()
        board = polling.read_task_board()
        active = [t for t in board if t.get("durum") not in ("done",)]
        done = len([t for t in board if t.get("durum") == "done"])
        quality = polling.read_quality_score()
        today = time.strftime("%Y-%m-%d %H:%M")

        lines = [f"<b>Periodik Durum - {html_escape(today)}</b>\n"]
        lines.append(f"Toplam gorev: {len(board)}")
        lines.append(f"Aktif: <b>{len(active)}</b> | Tamamlandi: <b>{done}</b>")
        lines.append(f"Kalite skoru: <b>{quality}</b>/100")

        if active:
            lines.append("\n<b>Aktif Gorevler:</b>")
            for t in active[:5]:
                lines.append(
                    f"  <code>{html_escape(t.get('task_id', '?'))}</code> "
                    f"[{html_escape(t.get('durum', ''))}]"
                    f" {html_escape(t.get('baslik', '')[:50])}"
                )
        lines.append(f"\n<i>{time.strftime('%H:%M:%S')}</i>")
        return "\n".join(lines)
    except Exception as exc:
        return f"<b>Periodik hata:</b> {html_escape(str(exc))}"


def run_once() -> dict:
    """Tek seferlik bildirim gonderir."""
    _load_env()
    token = _get_token()
    if not token:
        print("TELEGRAM_BOT_TOKEN bulunamadi.", file=sys.stderr)
        return {"ok": False, "error": "TOKEN not set"}

    chat_id = _get_chat_id()
    if not chat_id:
        print("TELEGRAM_CHAT_ID bulunamadi.", file=sys.stderr)
        return {"ok": False, "error": "CHAT_ID not set"}

    message = build_periodic_message()
    result = send_message(message)
    print(f"[{time.strftime('%H:%M:%S')}] Bildirim gonderildi: {result.get('ok')}", flush=True)
    return result


def run_loop(interval: int) -> None:
    """Sonsuz periodik dongu."""
    _load_env()
    enabled = os.environ.get("TELEGRAM_PERIODIC_ENABLED", "1") == "1"
    if not enabled:
        print("TELEGRAM_PERIODIC_ENABLED=0; periodic bot devredis.", file=sys.stderr)
        return

    print(f"Periodik bot baslatildi (interval={interval}s).", flush=True)
    while True:
        try:
            run_once()
        except Exception:
            print(f"[periodic] hata: {traceback.format_exc()}", file=sys.stderr)
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Telegram periodik durum botu"
    )
    parser.add_argument("--once", action="store_true",
                        help="Tek seferlik calistir")
    parser.add_argument("--interval", type=int,
                        default=int(os.environ.get(
                            "TELEGRAM_PERIODIC_INTERVAL_SECONDS", str(DEFAULT_INTERVAL)
                        )),
                        help=f"Bildirim araligi saniye (varsayilan: {DEFAULT_INTERVAL})")
    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        run_loop(args.interval)


if __name__ == "__main__":
    main()
