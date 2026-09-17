"""Test KPI history endpoint (/api/kpi/history)."""

import pytest
from unittest.mock import MagicMock, patch

from web_app import api_kpi_history


@pytest.fixture
def mock_engine():
    """Return a mock SQLAlchemy engine."""
    engine = MagicMock()
    # connect() returns a context manager; __enter__ returns the connection
    cm = MagicMock()
    cm.__enter__.return_value = MagicMock()
    cm.__exit__.return_value = None
    engine.connect.return_value = cm
    return engine


@pytest.fixture
def mock_connection():
    """Return a mock connection with sample data for both login and search queries."""
    conn = MagicMock()
    # Login query returns 5 columns: date, total_logins, successful_logins, signins, password_resets
    login_rows = [
        ("2026-09-17", 150, 45, 5, 2),
        ("2026-09-16", 120, 30, 3, 1),
        ("2026-09-15", 200, 80, 10, 3),
    ]
    # Search query returns 3 columns: date, total_searches, long_terms, very_long_terms
    search_rows = [
        ("2026-09-17", 50, 5, 1),
        ("2026-09-16", 40, 3, 0),
        ("2026-09-15", 60, 8, 2),
    ]

    # Create separate mock results for each execute call
    login_result = MagicMock()
    login_result.all.return_value = login_rows

    search_result = MagicMock()
    search_result.all.return_value = search_rows

    # execute() called twice: first for login, then for search
    conn.execute.side_effect = [login_result, search_result]
    return conn


def test_api_kpi_history_returns_structure(mock_engine, mock_connection):
    """Test that /api/kpi/history returns the expected structure."""
    # Configure the engine's connect() to return our mock connection
    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    with patch("web_app.get_engine", return_value=mock_engine):
        result = api_kpi_history(None, days=7)

    assert "period" in result
    assert "total_logins" in result
    assert "successful_logins" in result
    assert "signins" in result
    assert "password_resets" in result
    assert "search_events" in result
    assert "long_term_search" in result
    assert "very_long_term_search" in result
    assert "days" in result
    # Values should be integers
    assert isinstance(result["total_logins"], int)
    assert isinstance(result["successful_logins"], int)
    assert isinstance(result["signins"], int)
    assert isinstance(result["password_resets"], int)
    assert isinstance(result["search_events"], int)
    assert isinstance(result["long_term_search"], int)
    assert isinstance(result["very_long_term_search"], int)
    # Check computed values
    assert result["total_logins"] == 470  # 150+120+200
    assert result["successful_logins"] == 155  # 45+30+80
    assert result["signins"] == 18  # 5+3+10
    assert result["password_resets"] == 6  # 2+1+3
    assert result["search_events"] == 150  # 50+40+60
    assert result["long_term_search"] == 16  # 5+3+8
    assert result["very_long_term_search"] == 3  # 1+0+2


def test_api_kpi_history_empty_data(mock_engine, mock_connection):
    """Test that empty data returns zero values."""
    # Create connection that returns empty rows for both queries
    conn = MagicMock()
    empty_result = MagicMock()
    empty_result.all.return_value = []
    conn.execute.side_effect = [empty_result, empty_result]

    mock_engine.connect.return_value.__enter__.return_value = conn

    with patch("web_app.get_engine", return_value=mock_engine):
        result = api_kpi_history(None, days=7)

    assert result["total_logins"] == 0
    assert result["successful_logins"] == 0
    assert result["signins"] == 0
    assert result["password_resets"] == 0
    assert result["search_events"] == 0
    assert result["long_term_search"] == 0
    assert result["very_long_term_search"] == 0
    assert result["days"] == []


def test_api_kpi_history_exception_handling(mock_engine, mock_connection):
    """Test that exceptions during query are handled gracefully."""
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    # Simulate an exception during query execution
    mock_connection.execute.side_effect = Exception("Database error")

    with patch("web_app.get_engine", return_value=mock_engine):
        result = api_kpi_history(None, days=7)

    # Should still return a dict with default values (zeros)
    assert "period" in result
    assert "total_logins" in result
    assert result["total_logins"] == 0
    assert result["successful_logins"] == 0
    assert result["search_events"] == 0
