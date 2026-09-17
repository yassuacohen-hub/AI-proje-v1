# -*- coding: utf-8 -*-

from unittest.mock import Mock, patch

import pytest

from scripts import dash04_api_client as api_client
from scripts.dash04_api_client import APIError, get_api
from scripts.dash04_db_reader import read_only_query


def test_api_client_uses_env_url(monkeypatch, tmp_path):
    monkeypatch.delenv("DASH_API_URL", raising=False)
    monkeypatch.delenv("DASH_API_TOKEN", raising=False)
    monkeypatch.setattr(api_client, "CONFIG_PATH", tmp_path / "missing.toml")
    response = Mock(status_code=200)
    response.json.return_value = {}

    with patch("scripts.dash04_api_client.requests.get", return_value=response) as mock_get:
        assert get_api("/api/kpi") == {}

    assert mock_get.call_args.args[0] == "http://localhost:8000/api/kpi"


def test_api_client_api_error_on_non_select():
    with pytest.raises(ValueError):
        read_only_query("UPDATE companies SET legal_name = 'X'")


def test_read_only_query_rejects_insert():
    with pytest.raises(ValueError):
        read_only_query("INSERT INTO companies (legal_name) VALUES ('X')")


def test_get_api_import():
    assert callable(get_api)
    assert issubclass(APIError, Exception)


def test_read_only_query_import():
    assert callable(read_only_query)
