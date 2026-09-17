"""Test KPI history endpoint (/api/kpi/history)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from company_master.db.connection import get_engine
from web_app import api_kpi_history


@pytest.fixture
def mock_engine():
    """Return a mock SQLAlchemy engine."""
    engine = MagicMock()
    engine.connect.return_value = MagicMock()
    engine.connect.return_value.__enter__.return_value = MagicMock()
    engine.connect.return_value.__exit__.return_value = None
    return engine


@pytest.fixture
def mock_connection():
    """Return a mock connection with sample data."""
    conn = MagicMock()
    # Sample login data: 3 days of activity
    login_rows = [
        ("2026-09-17", 150, 45, 5),
        ("2026-09-16", 120, 30, 3),
        ("2026-09-15", 200, 80, 10),
    ]
    conn.execute.return_value = MagicMock()
    conn.execute.return_value.all.return_value = login_rows
    return conn


@pytest.fixture
def mock_response():
    """Return a mock response object."""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {}
    return resp


def test_api_kpi_history_returns_structure(mock_engine, mock_connection):
    """Test that /api/kpi/history returns the expected structure."""
    with patch("web_app.get_engine", return_value=mock_engine):
        with patch("web_app.engine.connect") as mock_connect:
            mock_connect.return_value = mock_connection
            result = api_kpi_history(None, days=7)
            assert "period" in result
            assert "total_logins" in result
            assert "successful_logins" in result
            assert "signins" in result
            assert "password_resets" in result
            assert "search_events" in result
            assert "long_term_search" in result
            assert "very_long_term_search" in result
            # Values should be integers
            assert isinstance(result["total_logins"], int)
            assert isinstance(result["successful_logins"], int)
            assert isinstance(result["signins"], int)
            assert isinstance(result["password_resets"], int)
            assert isinstance(result["search_events"], int)
            assert isinstance(result["long_term_search"], int)
            assert isinstance(result["very_long_term_search"], int)


def test_api_kpi_history_empty_data(mock_engine, mock_connection):
    """Test that empty data returns zero values."""
    with patch("web_app.get_engine", return_value=mock_engine):
        with patch("web_app.engine.connect") as mock_connect:
            mock_connect.return_value = mock_connection
            result = api_kpi_history(None, days=7)
            assert result["total_logins"] == 0
            assert result["successful_logins"] == 0
            assert result["signins"] == 0
            assert result["password_resets"] == 0
            assert result["search_events"] == 0
            assert result["long_term_search"] == 0
            assert result["very_long_term_search"] == 0


def test_api_kpi_history_exception_handling(mock_engine, mock_connection):
    """Test that exceptions during query are handled gracefully."""
    with patch("web_app.get_engine", return_value=mock_engine):
        with patch("web_app.engine.connect") as mock_connect:
            mock_connect.return_value = mock_connection
            # Simulate an exception during query execution
            mock_connection.execute.side_effect = Exception("Database error")
            result = api_kpi_history(None, days=7)
            # Should still return a dict with default values
            assert "period" in result
            assert "total_logins" in result
