"""Test KPI history endpoint (/api/kpi/history)."""

import pytest
from unittest.mock import MagicMock, patch

from web_app import api_kpi_history

@pytest.fixture
def mock_engine():
    engine = MagicMock()
    cm = MagicMock()
    cm.__enter__.return_value = MagicMock()
    cm.__exit__.return_value = None
    engine.connect.return_value = cm
    return engine

def _mock_conn(login_counts, search_counts, yf_counts, labels):
    conn = MagicMock()
    label_result = MagicMock()
    label_result.all.return_value = [(lbl,) for lbl in labels]
    login_result = MagicMock()
    login_result.all.return_value = [(lbl, c) for lbl, c in zip(labels, login_counts)]
    search_result = MagicMock()
    search_result.all.return_value = [(lbl, c) for lbl, c in zip(labels, search_counts)]
    yf_result = MagicMock()
    yf_result.all.return_value = [(lbl, c) for lbl, c in zip(labels, yf_counts)]
    conn.execute.side_effect = [label_result, login_result, search_result, yf_result]
    return conn

def test_api_kpi_history_returns_structure():
    labels = ["2026-09-11", "2026-09-12", "2026-09-13", "2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17"]
    conn = _mock_conn([150, 120, 200, 80, 90, 110, 130], [50, 40, 60, 30, 35, 45, 55], [5, 3, 8, 2, 4, 6, 9], labels)
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = conn
    with patch("web_app.get_engine", return_value=mock_engine):
        result = api_kpi_history(None, days=7)
    assert result["days"] == 7
    assert "series" in result
    assert "labels" in result
    assert result["series"]["login"] == [150, 120, 200, 80, 90, 110, 130]
    assert result["series"]["search"] == [50, 40, 60, 30, 35, 45, 55]
    assert result["series"]["yeni_firma"] == [5, 8, 16, 18, 22, 28, 37]
    assert result["labels"] == labels

def test_api_kpi_history_empty():
    labels = ["2026-09-11", "2026-09-12", "2026-09-13", "2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17"]
    conn = _mock_conn([], [], [], labels)
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = conn
    with patch("web_app.get_engine", return_value=mock_engine):
        result = api_kpi_history(None, days=7)
    assert result["series"]["login"] == [0, 0, 0, 0, 0, 0, 0]
    assert result["series"]["search"] == [0, 0, 0, 0, 0, 0, 0]
    assert result["series"]["yeni_firma"] == [0, 0, 0, 0, 0, 0, 0]

def test_api_kpi_history_days_validation():
    conn = MagicMock()
    conn.execute.return_value.all.return_value = []
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = conn
    with patch("web_app.get_engine", return_value=mock_engine):
        r0 = api_kpi_history(None, days=0)
        r31 = api_kpi_history(None, days=31)
        r7 = api_kpi_history(None, days=7)
    assert r0["days"] == 7
    assert r31["days"] == 7
    assert r7["days"] == 7

def test_api_kpi_history_exception_handling(mock_engine):
    mock_engine.connect.return_value.__enter__.return_value = MagicMock()
    mc = mock_engine.connect.return_value.__enter__.return_value
    mc.execute.side_effect = Exception("DB error")
    with patch("web_app.get_engine", return_value=mock_engine):
        result = api_kpi_history(None, days=7)
    assert result["days"] == 7
    assert result["series"]["login"] == []
    assert result["series"]["search"] == []
    assert result["series"]["yeni_firma"] == []
