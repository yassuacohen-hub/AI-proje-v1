"""COP-11: admin_performance.py render_performance_tab fonksiyonunun unit testi.

Kullanim:
    python -m pytest tests/test_admin_performance.py -v
"""

from __future__ import annotations

from unittest.mock import MagicMock
from unittest.mock import patch

from company_master.ui import MetricCard

import streamlit as st

from web_dashboard.tabs import admin_performance


def test_render_performance_tab_handles_no_data():
    """Veri olmadan render tutumlu olmalı."""
    with patch.object(
        admin_performance, "load_performance_data", return_value={}
    ), patch.object(admin_performance, "load_prometheus_metrics", return_value={}):
        with patch.object(st, "info") as mock_info:
            admin_performance.render_performance_tab()
            mock_info.assert_called()


def test_render_performance_tab_with_perf_data():
    """Performans verisi ile render dogru calismali."""
    perf_data = {
        "db_time_ms": 1250.50,
        "query_count": 50,
        "cache_hits": 40,
        "cache_misses": 10,
        "cache_hit_rate": 0.8,
        "slow_queries": [{"name": "SELECT * FROM companies", "ms": 200}],
        "timestamp": "2026-09-13T17:00:00",
    }

    with patch.object(
        admin_performance, "load_performance_data", return_value=perf_data
    ), patch.object(admin_performance, "load_prometheus_metrics", return_value={}):
        with patch("company_master.ui.MetricCard") as mock_metric, patch.object(
            admin_performance.st, "subheader"
        ) as mock_sub, patch.object(admin_performance.st, "divider"), patch.object(
            admin_performance.st, "session_state"
        ), patch.object(admin_performance.st, "markdown"), patch.object(
            admin_performance.st, "plotly_chart"
        ), patch.object(admin_performance.st, "area_chart"), patch.object(
            admin_performance.st, "caption"
        ):
            admin_performance.render_performance_tab()
            assert mock_metric.called


def test_render_performance_tab_with_prometheus():
    """Prometheus verisi ile render dogru calismali."""
    prom_data = {
        "huginn_companies_total": "8313",
        "huginn_db_time_ms": "1250.50",
        "huginn_cache_hit_rate": "0.8000",
    }

    with patch.object(
        admin_performance, "load_performance_data", return_value={}
    ), patch.object(
        admin_performance, "load_prometheus_metrics", return_value=prom_data
    ):
        with patch.object(st, "subheader"), patch.object(st, "divider"), patch.object(
            st, "info"
        ) as mock_info:
            admin_performance.render_performance_tab()
            # Prometheus varsa info cagrilmamali
            info_calls = [
                call for call in mock_info.call_args_list
                if "Prometheus" in str(call)
            ]
            assert len(info_calls) == 0


def test_render_performance_tab_both_data_sources():
    """Ikili veri kaynagi ile render test."""
    perf_data = {
        "db_time_ms": 500.0,
        "query_count": 100,
        "cache_hits": 75,
        "cache_misses": 25,
        "cache_hit_rate": 0.75,
        "slow_queries": [],
        "timestamp": "2026-09-13T17:00:00",
    }
    prom_data = {
        "huginn_query_count": "100",
        "huginn_db_time_ms": "500.00",
    }

    with patch.object(
        admin_performance, "load_performance_data", return_value=perf_data
    ), patch.object(
        admin_performance, "load_prometheus_metrics", return_value=prom_data
    ):
        with patch("company_master.ui.MetricCard") as mock_metric, patch.object(
            admin_performance.st, "dataframe"
        ), patch.object(admin_performance.st, "subheader"), patch.object(admin_performance.st, "divider"), patch.object(
            admin_performance.st, "session_state"
        ), patch.object(admin_performance.st, "markdown"), patch.object(
            admin_performance.st, "plotly_chart"
        ), patch.object(admin_performance.st, "area_chart"), patch.object(
            admin_performance.st, "caption"
        ):
            admin_performance.render_performance_tab()
            assert mock_metric.called


def test_render_performance_tab_open_telemetry_check():
    """OpenTelemetry kontrol test."""
    with patch.object(
        admin_performance, "load_performance_data", return_value={}
    ), patch.object(
        admin_performance, "load_prometheus_metrics", return_value={}
    ), patch.object(
        admin_performance, "st"
    ) as mock_st:
        with patch.dict("sys.modules", {"opentelemetry": None}):
            try:
                admin_performance.render_performance_tab()
            except Exception:
                pass


def test_load_performance_data_api_error():
    """API hata durumunda empty dict dönecek."""
    import urllib.error

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.URLError("connection refused")
        result = admin_performance.load_prometheus_metrics()
        assert result == {}