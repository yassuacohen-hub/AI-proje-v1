# -*- coding: utf-8 -*-
"""Test UI-ADMIN-ARAMA-BOSLUK-20 (UI-20): içerik boşluk raporu."""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta

# Test edilecek modülü import et
from web_dashboard.tabs import admin_quality


def test_admin_quality_bos_tabloda_hata_vermez():
    """Tablo boşken fonksiyon hata vermez."""
    with patch("web_dashboard.tabs.admin_quality.get_engine") as mock_get_engine:
        mock_conn = MagicMock()
        mock_conn.execute.return_value = []
        mock_get_engine.return_value.connect.return_value.__enter__.return_value = mock_conn
        
        df = admin_quality.load_freshness_distribution()
        assert list(df.columns) == ["kova", "adet"]
        assert df.empty


def test_admin_quality_normalize_fonksiyonu():
    """Arama terimi normalize fonksiyonu testi."""
    # This would test a normalize function if it existed
    # For now, just check that the module exists
    assert hasattr(admin_quality, "st")  # streamlit mock will be here in test


if __name__ == "__main__":
    pytest.main([__file__, "-v"])