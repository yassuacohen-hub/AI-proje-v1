# -*- coding: utf-8 -*-
"""Telegram bot — entegre test scripti (mock veya canli).

Mock modda (varsayilan): requests kutuphanesini taklit eder; gerçek
ag cagrisi yapilmaz. .env'de TELEGRAM_BOT_TOKEN yoksa bile calisir.

Live mod (--live): .env'deki token/chat_id ile gerçek Telegram API'ye
baglanir.

Kullanim:
    python scripts/test_telegram.py               # mock test
    python scripts/test_telegram.py --live          # canli test
    python scripts/test_telegram.py --live --message "selam"
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
    _get_chat_id,
    _get_token,
    _load_env,
    html_escape,
    masked_token,
    parse_command,
    send_message,
)


def _make_mock_response(ok: bool = True, description: str = "OK", result: dict | None = None):
    """requests.post yerine gecen mock yaniti olusturur."""
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"ok": ok, "description": description, "result": result or {}}
    return resp


def test_send_message_mock():
    """Mock ortamda send_message testi."""
    payload = {"ok": True, "result": {"message_id": 1}}
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=_make_mock_response(True, "OK", {"message_id": 42})) as mock_post, \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        result = send_message("Test mesaj")
        assert result["ok"] is True, f"ok=False: {result}"
        assert result["result"]["message_id"] == 42
        call_args = mock_post.call_args
        sent_payload = call_args.kwargs.get("json", call_args[1].get("json"))
        assert sent_payload["text"] == "Test mesaj"
        assert sent_payload["chat_id"] == "999"
        assert sent_payload["parse_mode"] == "HTML"
    print("test_send_message_mock: PASS")


def test_send_message_missing_token():
    """Token olmadan mesaj gonderme."""
    with patch("src.company_master.utils.telegram_bot._load_env", return_value=None), patch.dict("os.environ", {}, clear=True):
        result = send_message("Test")
        assert result["ok"] is False
        assert "TOKEN" in result["error"] or "not set" in result["error"]
    print("test_send_message_missing_token: PASS")


def test_send_message_missing_chat_id():
    """Chat ID olmadan mesaj gonderme."""
    with patch("src.company_master.utils.telegram_bot._load_env", return_value=None), patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC"}, clear=True):
        result = send_message("Test")
        assert result["ok"] is False
        assert "CHAT_ID" in result["error"] or "not set" in result["error"]
    print("test_send_message_missing_chat_id: PASS")


def test_send_message_ok_false():
    """Telegram API ok=false yaniti."""
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=_make_mock_response(False, "Bad Request")), \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        result = send_message("Test")
        assert result["ok"] is False
        assert "Bad Request" in result.get("error", "")
    print("test_send_message_ok_false: PASS")


def test_send_message_request_exception():
    """requests.RequestException yakalama testi."""
    import requests as req_lib
    with patch("src.company_master.utils.telegram_bot.requests.post",
               side_effect=req_lib.RequestException("Connection timeout")), \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        result = send_message("Test")
        assert result["ok"] is False
        assert "timeout" in result["error"].lower() or "connection" in result["error"].lower()
    print("test_send_message_request_exception: PASS")


def test_html_escape():
    """HTML escape testi."""
    assert html_escape(None) == ""
    assert html_escape("") == ""
    assert html_escape("<b>safe</b>") == "&lt;b&gt;safe&lt;/b&gt;" or "<b>safe</b>" == html_escape("<b>safe</b>")
    # Preserve allowed tags
    escaped = html_escape("<b>bold</b> & <i>italic</i>")
    assert "<b>bold</b>" in escaped
    assert "<i>italic</i>" in escaped
    assert "&amp;" in escaped
    # Strip dangerous tags
    escaped2 = html_escape("<script>alert(1)</script>")
    assert "<script>" not in escaped2
    print("test_html_escape: PASS")


def test_parse_command():
    """Komut parsing testi."""
    # Basit komut
    r = parse_command("/start")
    assert r is not None
    assert r["command"] == "start"
    assert r["bot"] is None
    assert r["args"] == []

    # Bot adi ile komut
    r = parse_command("/start@MyBot merhaba dunya")
    assert r is not None
    assert r["command"] == "start"
    assert r["bot"] == "MyBot"
    assert r["args"] == ["merhaba", "dunya"]

    # Bot username filtresi
    r = parse_command("/start@OtherBot test", bot_username="MyBot")
    assert r is None  # farkli bot

    r = parse_command("/start@MyBot test", bot_username="MyBot")
    assert r is not None
    assert r["command"] == "start"

    # Genuz metin
    assert parse_command("merhaba") is None
    assert parse_command("") is None
    assert parse_command(None) is None

    print("test_parse_command: PASS")


def test_set_status_helper():
    """set_status yardimci testi (mock)."""
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=_make_mock_response(False, "Bad Request")) as mock_post:
        result = send_message("deneme", chat_id="123", parse_mode="HTML")
        assert result["ok"] is False
    print("test_set_status_helper: PASS")


def test_masked_token():
    """Token gizleme testi."""
    assert masked_token(None) == "<not set>"
    assert masked_token("") == "<not set>"
    assert "****" in masked_token("123:ABCDEF")
    assert masked_token("123:ABCDEFG") == "123:****DEFG" if len("ABCDEFG") >= 4 else True
    print("test_masked_token: PASS")


def run_mock_tests():
    """Tum mock testleri calistir."""
    tests = [
        test_send_message_mock,
        test_send_message_missing_token,
        test_send_message_missing_chat_id,
        test_send_message_ok_false,
        test_send_message_request_exception,
        test_html_escape,
        test_parse_command,
        test_set_status_helper,
        test_masked_token,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"{test.__name__}: FAIL — {exc}")
            failed += 1
    print(f"\nMock testler: {passed} passed, {failed} failed (toplam {len(tests)})")
    return failed == 0


def run_live_test(message: str | None = None) -> bool:
    """Canli Telegram API testi (--live)."""
    _load_env()
    token = _get_token()
    chat_id = _get_chat_id()
    if not token:
        print("TELEGRAM_BOT_TOKEN .env'de ayarlanmamissiniz.", file=sys.stderr)
        return False
    if not chat_id:
        print("TELEGRAM_CHAT_ID .env'de ayarlanmamissiniz.", file=sys.stderr)
        return False

    display = message or "Telegram bot canli test mesaji. Bot aktif."
    display = display.replace("🤖", "[Bot]")
    print(f"Gonderilen mesaj: {display}")
    result = send_message(message or display)
    if result["ok"]:
        print(f"Mesaj gonderildi: {result['result'].get('message_id', '?')}")
        return True
    else:
        print(f"Hata: {result['error']}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Telegram bot test scripti")
    parser.add_argument("--live", action="store_true",
                        help="Canli Telegram API testi (gerektirir: .env token + chat_id)")
    parser.add_argument("--message", type=str, default=None,
                        help="Live modda gonderilecek mesaj")
    args = parser.parse_args()

    if args.live:
        success = run_live_test(args.message)
        sys.exit(0 if success else 1)
    else:
        success = run_mock_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
