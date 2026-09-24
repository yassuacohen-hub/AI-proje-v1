"""Unit tests for the Telegram message sender."""

from unittest.mock import MagicMock, patch

import requests

import src.company_master.utils.telegram_bot as telegram_bot


def _response(data):
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = data
    return response


def test_send_message_posts_expected_payload():
    telegram_bot.TOKEN = "123:ABC"
    telegram_bot.CHAT_ID = "999"
    telegram_bot.API_URL = "https://api.telegram.org/bot123:ABC"
    response_data = {"ok": True, "result": {"message_id": 42}}

    with patch.object(telegram_bot.requests, "post", return_value=_response(response_data)) as post:
        result = telegram_bot.send_message("Merhaba")

    assert result == response_data
    post.assert_called_once_with(
        "https://api.telegram.org/bot123:ABC/sendMessage",
        json={
            "chat_id": "999",
            "text": "Merhaba",
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=telegram_bot.DEFAULT_TIMEOUT,
    )


def test_send_message_uses_explicit_chat_id_and_options():
    telegram_bot.TOKEN = "123:ABC"
    telegram_bot.CHAT_ID = "999"

    with patch.object(telegram_bot.requests, "post", return_value=_response({"ok": True})) as post:
        telegram_bot.send_message(
            "<b>Merhaba</b>",
            chat_id="111",
            parse_mode="Markdown",
            disable_web_page_preview=False,
        )

    payload = post.call_args.kwargs["json"]
    assert payload == {
        "chat_id": "111",
        "text": "<b>Merhaba</b>",
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }


def test_send_message_returns_error_when_token_is_missing():
    telegram_bot.TOKEN = None
    telegram_bot.CHAT_ID = "999"

    result = telegram_bot.send_message("test")

    assert result == {"ok": False, "error": "TOKEN not set"}


def test_send_message_returns_request_error():
    telegram_bot.TOKEN = "123:ABC"
    telegram_bot.CHAT_ID = "999"

    with patch.object(
        telegram_bot.requests,
        "post",
        side_effect=requests.RequestException("connection refused"),
    ):
        result = telegram_bot.send_message("test")

    assert result == {"ok": False, "error": "connection refused"}
