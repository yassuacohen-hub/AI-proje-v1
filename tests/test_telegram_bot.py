# -*- coding: utf-8 -*-
"""Unit tests for src/company_master/utils/telegram_bot.py.

Hiçbir test gerçek Telegram API'sine baglanmaz; requests.post
ve os.environ monkeypatch ile gecilir. _load_env no-op yapilir
boylece .env'deki gercek tokenlar testleri etkilemez.
"""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests as req_lib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.company_master.utils.telegram_bot import (
    DEFAULT_TIMEOUT,
    _get_chat_id,
    _get_token,
    _load_env,
    get_updates,
    html_escape,
    is_authorized,
    masked_token,
    parse_command,
    send_alert,
    send_daily_summary,
    send_message,
    send_status_report,
    send_task_completed,
    send_task_started,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clear_telegram_env(monkeypatch):
    """Testler oncesi Telegram env degiskenlerini temizle ve _load_env'i no-op yap.

    .env dosyasindaki gercek tokenlarin testleri etkilememesi icin
    _load_env fonksiyonunu (load_dotenv cagrisini) bypass ederiz.
    """
    for key in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "TELEGRAM_BOT_USERNAME"):
        monkeypatch.delenv(key, raising=False)
    import src.company_master.utils.telegram_bot as tb_mod
    monkeypatch.setattr(tb_mod, "_load_env", lambda: None)
    yield


# ---------------------------------------------------------------------------
# send_message tests
# ---------------------------------------------------------------------------

def _mock_response(ok=True, description="OK", result=None):
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"ok": ok, "description": description, "result": result or {}}
    return resp


@pytest.mark.parametrize("payload_text", [
    "Merhaba",
    "<b>Kalin</b>",
    "Turkce karakter: c g i I o s u",
    "",
])
def test_send_message_success(payload_text):
    """send_message basarili gonderimde ok=True doner."""
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=_mock_response(True, "OK", {"message_id": 42})) as mock_post, \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        result = send_message(payload_text)
        assert result["ok"] is True
        assert result["result"]["message_id"] == 42
        sent = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
        assert sent["chat_id"] == "999"
        assert sent["text"] == payload_text
        assert sent["parse_mode"] == "HTML"


def test_send_message_missing_token():
    """Token eksikse hata doner."""
    result = send_message("test")
    assert result["ok"] is False
    assert "TOKEN" in result["error"] or "not set" in result["error"]


def test_send_message_missing_chat_id():
    """Chat ID eksikse hata doner (token var ama chat_id yok)."""
    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC"}):
        result = send_message("test")
        assert result["ok"] is False
        assert "CHAT_ID" in result["error"] or "not set" in result["error"]


def test_send_message_ok_false():
    """Telegram API ok=false yaniti."""
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=_mock_response(False, "Bad Request: chat not found")), \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        result = send_message("test")
        assert result["ok"] is False
        assert "Bad Request" in result["error"]
        assert result.get("raw", {}).get("ok") is False


def test_send_message_request_exception():
    """requests.RequestException yakalanir."""
    with patch("src.company_master.utils.telegram_bot.requests.post",
               side_effect=req_lib.ConnectionError("Connection refused")), \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        result = send_message("test")
        assert result["ok"] is False
        assert "refused" in result["error"].lower() or "connection" in result["error"].lower()


def test_send_message_timeout_exception():
    """Timeout yakalanir."""
    with patch("src.company_master.utils.telegram_bot.requests.post",
               side_effect=req_lib.Timeout("timeout")), \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        result = send_message("test")
        assert result["ok"] is False
        assert "timeout" in result["error"].lower()


def test_send_message_json_decode_error():
    """JSON decode hatasi yakalanir."""
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=mock_resp), \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        result = send_message("test")
        assert result["ok"] is False
        assert "JSON" in result["error"] or "decode" in result["error"].lower()


def test_send_message_uses_explicit_chat_id():
    """explicit chat_id override eder."""
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=_mock_response(True, "OK", {"message_id": 1})) as mock_post, \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        send_message("test", chat_id="111")
        sent = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
        assert sent["chat_id"] == "111"


def test_send_message_timeout_param():
    """requests timeout parametresi gonderilir."""
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=_mock_response()) as mock_post, \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        send_message("test")
        assert mock_post.call_args.kwargs.get("timeout") == DEFAULT_TIMEOUT


# ---------------------------------------------------------------------------
# html_escape tests
# ---------------------------------------------------------------------------

def test_html_escape_none_and_empty():
    assert html_escape(None) == ""
    assert html_escape("") == ""


def test_html_escape_preserves_allowed_tags():
    """b, i, u, code, pre, a gibi etiketler korunur."""
    e = html_escape("<b>bold</b> <i>italic</i> <code>code</code>")
    assert "<b>bold</b>" in e
    assert "<i>italic</i>" in e
    assert "<code>code</code>" in e


def test_html_escape_strips_dangerous_tags():
    """script gibi tehlikeli etiketler escape edilir, tag kapanir."""
    e = html_escape("<script>alert(1)</script>")
    assert "<script>" not in e
    assert "&lt;script&gt;" in e


def test_html_escape_escapes_special_chars():
    e = html_escape("a & b < c > d e f")
    assert "&amp;" in e
    assert "&lt;" in e
    assert "&gt;" in e


def test_html_escape_turkish_chars():
    """Turkce karakterler bozulmadan korunur."""
    e = html_escape("c g i I o s u")
    assert "c" in e


def test_html_escape_preserves_custom_tags():
    """Ozel preserve_tags verildiginde o etiketler korunur."""
    e = html_escape("<b>bold</b>", preserve_tags=())
    assert "<b>bold</b>" in e


# ---------------------------------------------------------------------------
# parse_command tests
# ---------------------------------------------------------------------------

def test_parse_command_basic():
    r = parse_command("/start")
    assert r is not None
    assert r["command"] == "start"
    assert r["bot"] is None
    assert r["args"] == []


def test_parse_command_with_bot_name():
    r = parse_command("/help@MyBot arg1 arg2")
    assert r is not None
    assert r["command"] == "help"
    assert r["bot"] == "MyBot"
    assert r["args"] == ["arg1", "arg2"]


def test_parse_command_with_bot_filter():
    """bot_username verildiginde farkli bot filtrelenir."""
    r = parse_command("/start@OtherBot", bot_username="MyBot")
    assert r is None


def test_parse_command_matching_bot_name():
    r = parse_command("/start@MyBot", bot_username="MyBot")
    assert r is not None
    assert r["command"] == "start"


def test_parse_command_non_command():
    assert parse_command("merhaba") is None
    assert parse_command("") is None
    assert parse_command(None) is None


def test_parse_command_set_status():
    r = parse_command("/set_status TG-01 done")
    assert r is not None
    assert r["command"] == "set_status"
    assert r["args"] == ["TG-01", "done"]


def test_parse_command_case_insensitive():
    r = parse_command("/START")
    assert r is not None
    assert r["command"] == "start"  # kucuk harfe donusur


# ---------------------------------------------------------------------------
# is_authorized tests
# ---------------------------------------------------------------------------

def test_is_authorized_none_chat():
    assert is_authorized(None) is False


def test_is_authorized_no_env_chat_id():
    """Env'de chat_id yok -> yetkisiz."""
    assert is_authorized("123") is False


def test_is_authorized_match(monkeypatch):
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "999")
    assert is_authorized("999") is True


def test_is_authorized_mismatch(monkeypatch):
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "999")
    assert is_authorized("111") is False


def test_is_authorized_explicit_target():
    """explicit allowed_chat_id override eder."""
    assert is_authorized("123", allowed_chat_id="123") is True
    assert is_authorized("999", allowed_chat_id="123") is False


def test_is_authorized_string_vs_int(monkeypatch):
    """String/int karisik tiplerde esitlik kontrolu."""
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    assert is_authorized(123) is True


# ---------------------------------------------------------------------------
# get_updates tests
# ---------------------------------------------------------------------------

def test_get_updates_missing_token():
    result = get_updates()
    assert result["ok"] is False
    assert "TOKEN" in result["error"]


def test_get_updates_success():
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "ok": True,
        "result": [
            {"update_id": 100, "message": {"message_id": 1, "chat": {"id": "999"},
                                            "text": "/start"}},
        ],
    }
    with patch("src.company_master.utils.telegram_bot.requests.get",
               return_value=mock_resp) as mock_get, \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC"}):
        result = get_updates(offset=0, timeout=30, limit=100)
        assert result["ok"] is True
        assert len(result["result"]) == 1
        assert result["next_offset"] == 101  # max update_id + 1
        assert mock_get.call_args.kwargs.get("timeout") == 40  # timeout + 10


def test_get_updates_request_exception():
    with patch("src.company_master.utils.telegram_bot.requests.get",
               side_effect=req_lib.ConnectionError("dns")), \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC"}):
        result = get_updates()
        assert result["ok"] is False
        assert "dns" in result["error"].lower() or "connection" in result["error"].lower()


# ---------------------------------------------------------------------------
# Helper functions tests
# ---------------------------------------------------------------------------

def test_send_task_started_escapes():
    """send_task_started HTML escape uygular."""
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=_mock_response(True, "OK", {"message_id": 1})) as mock_post, \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        result = send_task_started("Test Gorev & <script>", "kilo")
        assert result["ok"] is True
        sent = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
        assert "<script>" not in sent["text"]
        assert "Test Gorev" in sent["text"]


def test_send_task_completed_escapes():
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=_mock_response(True, "OK", {"message_id": 1})) as mock_post, \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        result = send_task_completed("Gorev", "agent", "Ozet <b>mesaj</b>")
        assert result["ok"] is True
        sent = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
        assert "<b>mesaj</b>" in sent["text"]


def test_send_alert_escapes():
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=_mock_response(True, "OK", {"message_id": 1})) as mock_post, \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        result = send_alert("Baslik & <x>", "Mesaj icerigi")
        assert result["ok"] is True
        sent = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
        assert "&amp;" in sent["text"]


def test_send_daily_summary():
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=_mock_response(True, "OK", {"message_id": 1})) as mock_post, \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        result = send_daily_summary({"total_firms": 1000, "new_firms": 50,
                                      "avg_quality": 65.5, "active_tasks": 3,
                                      "completed_tasks": 10})
        assert result["ok"] is True
        sent = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
        assert "1,000" in sent["text"]
        assert "65.5" in sent["text"]


def test_send_status_report():
    with patch("src.company_master.utils.telegram_bot.requests.post",
               return_value=_mock_response(True, "OK", {"message_id": 1})) as mock_post, \
         patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123:ABC", "TELEGRAM_CHAT_ID": "999"}):
        result = send_status_report({"key": "value <x>", "status": "OK"})
        assert result["ok"] is True
        sent = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
        assert "<x>" not in sent["text"]


# ---------------------------------------------------------------------------
# masked_token tests
# ---------------------------------------------------------------------------

def test_masked_token_not_set():
    assert masked_token(None) == "<not set>"
    assert masked_token("") == "<not set>"


def test_masked_token_format():
    m = masked_token("123:ABCDEFGH")
    assert m.startswith("123:")
    assert "****" in m
    assert "EFGH" in m


def test_masked_token_short():
    m = masked_token("abc")
    assert "****" in m
