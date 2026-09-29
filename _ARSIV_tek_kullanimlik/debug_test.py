#!/usr/bin/env python3
"""
Debug test to see actual call args
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from unittest.mock import MagicMock, patch
from web_app import aktivite_yaz


def make_mock_conn():
    """Mock connection that works as context manager."""
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=None)
    return mock_conn


def make_mock_engine(mock_conn):
    """Mock engine that returns mock_conn on connect()."""
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    return mock_engine


mock_conn = make_mock_conn()
mock_engine = make_mock_engine(mock_conn)

with patch('web_app.get_engine', return_value=mock_engine):
    aktivite_yaz(
        user_id="test-user",
        olay_tipi="giris",
        detay={"ip": "127.0.0.1"},
        basarili=True,
    )

print("call_count:", mock_conn.execute.call_count)
print("call_args:", mock_conn.execute.call_args)
print("call_args_list:", mock_conn.execute.call_args_list)