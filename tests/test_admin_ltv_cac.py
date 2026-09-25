#!/usr/bin/env python3
"""LTV/CAC Testleri — UI-ADMIN-LTV-CAC-27"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta


def test_calculate_ltv_basic():
    """LTV hesaplama testi."""
    from web_app import _calculate_ltv

    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None
    
    # Mock revenue query
    mock_revenue_result = Mock()
    mock_revenue_result.scalar.return_value = 10000.0
    
    # Mock active users query
    mock_active_result = Mock()
    mock_active_result.scalar.return_value = 50
    
    mock_conn.execute.side_effect = [mock_revenue_result, mock_active_result]
    
    mock_engine = Mock()
    mock_engine.connect.return_value = mock_conn

    with patch('web_app.get_engine', return_value=mock_engine):
        with patch('web_app.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2026, 9, 25)
            ltv = _calculate_ltv(30)
            # 10000 revenue / 50 active = 200
            assert ltv == 200.0

    print("[TEST] calculate_ltv_basic: PASSED")


def test_calculate_cac_basic():
    """CAC hesaplama testi."""
    from web_app import _calculate_cac

    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None
    
    # Mock new users query
    mock_new_users = Mock()
    mock_new_users.scalar.return_value = 100
    
    mock_conn.execute.return_value = mock_new_users
    
    mock_engine = Mock()
    mock_engine.connect.return_value = mock_conn

    with patch('web_app.get_engine', return_value=mock_engine):
        with patch('web_app.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2026, 9, 25)
            with patch('web_app.os.getenv', return_value="50000"):
                cac = _calculate_cac(30)
                # 50000 / 100 = 500
                assert cac == 500.0

    print("[TEST] calculate_cac_basic: PASSED")


def test_ltv_cac_trend():
    """Trend verisi testi."""
    from web_app import _ltv_cac_trend

    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None
    
    # Mock revenue rows
    mock_revenue_result = Mock()
    mock_revenue_result.mappings.return_value.all.return_value = [
        {"date": "2026-09-20", "daily_revenue": 1000.0},
        {"date": "2026-09-21", "daily_revenue": 1500.0},
    ]
    
    # Mock new user rows
    mock_user_result = Mock()
    mock_user_result.mappings.return_value.all.return_value = [
        {"date": "2026-09-20", "new_users": 5},
        {"date": "2026-09-21", "new_users": 3},
    ]
    
    mock_conn.execute.side_effect = [mock_revenue_result, mock_user_result]
    
    mock_engine = Mock()
    mock_engine.connect.return_value = mock_conn

    with patch('web_app.get_engine', return_value=mock_engine):
        with patch('web_app.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2026, 9, 22)
            with patch('web_app.os.getenv', return_value="50000"):
                trend = _ltv_cac_trend(180)
                assert isinstance(trend, list)
                assert len(trend) == 180
                # Check structure
                for entry in trend:
                    assert "date" in entry
                    assert "ltv" in entry
                    assert "cac" in entry
                    assert "ratio" in entry

    print("[TEST] ltv_cac_trend: PASSED")


def test_ltv_cac_by_tier():
    """Tier breakdown testi."""
    from web_app import _ltv_cac_by_tier

    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None
    
    # Mock queries for each tier
    mock_conn.execute.side_effect = [
        Mock(scalar=Mock(return_value=5000)),   # terminal revenue
        Mock(scalar=Mock(return_value=10)),     # terminal user count
        Mock(scalar=Mock(return_value=2)),      # terminal new users
        Mock(scalar=Mock(return_value=50000)),  # strategic revenue
        Mock(scalar=Mock(return_value=5)),      # strategic user count
        Mock(scalar=Mock(return_value=1)),      # strategic new users
        Mock(scalar=Mock(return_value=500000)), # enterprise revenue
        Mock(scalar=Mock(return_value=2)),      # enterprise user count
        Mock(scalar=Mock(return_value=1)),      # enterprise new users
    ]
    
    mock_engine = Mock()
    mock_engine.connect.return_value = mock_conn

    with patch('web_app.get_engine', return_value=mock_engine):
        with patch('web_app.os.getenv', return_value="50000"):
            by_tier = _ltv_cac_by_tier()
            assert "terminal" in by_tier
            assert "strategic" in by_tier
            assert "enterprise" in by_tier
            
            for tier_data in by_tier.values():
                assert "ltv" in tier_data
                assert "cac" in tier_data
                assert "ratio" in tier_data

    print("[TEST] ltv_cac_by_tier: PASSED")


def test_api_ltv_cac_endpoint():
    """API endpoint testi."""
    from web_app import api_admin_ltv_cac

    with patch('web_app._calculate_ltv', return_value=12500.50):
        with patch('web_app._calculate_cac', return_value=850.0):
            with patch('web_app._ltv_cac_trend', return_value=[{"date": "2026-09-24", "ltv": 12400, "cac": 860, "ratio": 14.4}]):
                with patch('web_app._ltv_cac_by_tier', return_value={
                    "terminal": {"ltv": 500, "cac": 200, "ratio": 2.5},
                    "strategic": {"ltv": 5000, "cac": 800, "ratio": 6.25},
                    "enterprise": {"ltv": 50000, "cac": 1500, "ratio": 33.3}
                }):
                    result = api_admin_ltv_cac(days=30, _auth="admin")
                    assert result["ltv"] == 12500.50
                    assert result["cac"] == 850.0
                    assert result["ratio"] == round(12500.50 / 850.0, 2)
                    assert len(result["trend"]) == 1
                    assert "terminal" in result["by_tier"]
                    assert "strategic" in result["by_tier"]
                    assert "enterprise" in result["by_tier"]

    print("[TEST] api_admin_ltv_cac_endpoint: PASSED")


if __name__ == "__main__":
    test_calculate_ltv_basic()
    test_calculate_cac_basic()
    test_ltv_cac_trend()
    test_ltv_cac_by_tier()
    test_api_ltv_cac_endpoint()
    print("\n[TUM TESTLER GECTI]")
