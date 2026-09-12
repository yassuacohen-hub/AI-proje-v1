# -*- coding: utf-8 -*-
"""Telegram bot — basit test scripti.

Mock bazli, harici bagimlilik yok. requests.post ve env degiskenleri
gecilir; .env gerekmez.

Kullanim:
    python scripts/test_telegram_simple.py
    python scripts/test_telegram_simple.py --live
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT))

from src.company_master.utils.telegram_bot import (
    html_escape,
    masked_token,
    parse_command,
    send_message,
)


def _ok_response(result: dict | None = None) -> MagicMock:
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"ok": True, "result": result or {"message_id": 1}}
    return resp


def test_basic_send_message():
    """Temel send_message mock testi."""
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=_ok_response({"message_id": 99})), \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "test:token", "TELEGRAM_CHAT_ID": "555"}):
        r = send_message("selam")
        assert r["ok"] is True
    print("basic_send_message: OK")


def test_escape_preserves_tags():
    """html_escape duvar gapli etiketleri korur."""
    e = html_escape("<b>Kalin</b> ve <i>egik</i> & karakter")
    assert "<b>Kalin</b>" in e
    assert "<i>egik</i>" in e
    assert "&amp;" in e
    print("escape_preserves_tags: OK")


def test_escape_strips_script():
    """html_escape script tag'ini sanitize eder."""
    e = html_escape('<script>alert("xss")</script>')
    assert "<script>" not in e
    print("escape_strips_script: OK")


def test_parse_simple_command():
    """Komut parsing - basit."""
    p = parse_command("/status")
    assert p and p["command"] == "status"
    print("parse_simple_command: OK")


def test_parse_command_with_args():
    """Komut parsing - argumanli."""
    p = parse_command("/set_status TG-01 done extra_arg")
    assert p and p["command"] == "set_status"
    assert p["args"] == ["TG-01", "done", "extra_arg"]
    print("parse_command_with_args: OK")


def test_parse_command_bot_filter():
    """Komut parsing - bot adi filtreleme."""
    p = parse_command("/start@OtherBot", bot_username="MyBot")
    assert p is None
    p2 = parse_command("/start@MyBot", bot_username="MyBot")
    assert p2 is not None
    print("parse_command_bot_filter: OK")


def test_no_token():
    """Token yokken hata doner."""
    with patch("src.company_master.utils.telegram_bot._load_env", return_value=None), patch.dict("os.environ", {}, clear=True):
        r = send_message("test")
        assert r["ok"] is False and "not set" in r.get("error", "TOKEN")
    print("no_token: OK")


def test_masked_token_hide():
    """Token gizleme."""
    assert masked_token("123:abcdef") == "123:****cdef"
    print("masked_token_hide: OK")


TESTS = [
    test_basic_send_message,
    test_escape_preserves_tags,
    test_escape_strips_script,
    test_parse_simple_command,
    test_parse_command_with_args,
    test_parse_command_bot_filter,
    test_no_token,
    test_masked_token_hide,
]


def run_live(token: str, chat_id: str, message: str) -> bool:
    """Canli test (gerçek API)."""
    import requests as req
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = req.post(url, json={"chat_id": chat_id, "text": message,
                                    "parse_mode": "HTML"}, timeout=30)
        data = resp.json()
        if data.get("ok"):
            print(f"Canli mesaj gonderildi (msg_id: {data['result']['message_id']})")
            return True
        print(f"API hata: {data.get('description')}")
        return False
    except Exception as exc:
        print(f"Baglanti hatasi: {exc}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Telegram bot basit testleri")
    parser.add_argument("--live", action="store_true", help="Canli test")
    args = parser.parse_args()

    if args.live:
        from src.company_master.utils.telegram_bot import _load_env, _get_token, _get_chat_id
        _load_env()
        token = _get_token()
        chat_id = _get_chat_id()
        if not token or not chat_id:
            print("Token veya chat_id eksik. --live icin .env gerekir.", file=sys.stderr)
            sys.exit(1)
        ok = run_live(token, chat_id, "🤖 Basit canli test mesaji.")
        sys.exit(0 if ok else 1)

    passed = 0
    failed = 0
    for test in TESTS:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"{test.__name__}: FAILED — {exc}")
            failed += 1
    print(f"\n{passed}/{passed + failed} test gecti.")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
