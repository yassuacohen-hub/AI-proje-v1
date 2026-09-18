# -*- coding: utf-8 -*-
"""Unit tests for scripts/detect_st_metric.py (ADMIN-KPI-KART-02)."""
import ast
import tempfile
from pathlib import Path

import pytest

from scripts.detect_st_metric import StMetricVisitor, find_st_metric_in_file


def test_visitor_detects_st_metric():
    """Visitor `st.metric` cagrisini tespit etmelidir."""
    code = """
import streamlit as st

def render():
    st.metric("Label", 123)
    st.metric("Label2", "456", delta="10")
"""

    tree = ast.parse(code)
    visitor = StMetricVisitor()
    visitor.visit(tree)

    assert len(visitor.st_metric_calls) == 2
    assert visitor.st_metric_calls[0]["lineno"] == 5
    assert visitor.st_metric_calls[1]["lineno"] == 6


def test_visitor_ignores_kpi_karti():
    """Visitor `kpi_karti` cagrisini goz ardi etmelidir."""
    code = """
from web_dashboard.charts import kpi_karti

def render():
    kpi_karti("Label", 123)
    kpi_karti("Label2", "456", delta="10")
"""

    tree = ast.parse(code)
    visitor = StMetricVisitor()
    visitor.visit(tree)

    assert len(visitor.st_metric_calls) == 0


def test_visitor_ignores_other_st_calls():
    """Visitor baska `st.` cagrilari (st.subheader, st.caption, vb.) goz ardi etmelidir."""
    code = """
import streamlit as st

def render():
    st.subheader("Baslik")
    st.caption("Alt baslik")
    st.info("Bilgi")
    st.error("Hata")
"""

    tree = ast.parse(code)
    visitor = StMetricVisitor()
    visitor.visit(tree)

    assert len(visitor.st_metric_calls) == 0


def test_find_st_metric_in_file(tmp_path):
    """Dosya tabanli tespit calismalidir."""
    test_file = tmp_path / "test_tab.py"
    test_file.write_text("""
import streamlit as st

def render():
    st.metric("Metrik 1", 100)
    st.metric("Metrik 2", 200)
""", encoding="utf-8")

    results = find_st_metric_in_file(test_file)
    assert len(results) == 2
    assert results[0]["lineno"] == 5
    assert results[1]["lineno"] == 6


def test_webhook_monitor_no_st_metric():
    """webhook_monitor.py dosyasinda `st.metric` yokmalidir (ADMIN-KPI-KART-02 sonrasi)."""
    # Bu test ADMIN-KPI-KART-02 tamamlandiktan sonra gecmeli
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    webhook_file = ROOT / "web_dashboard" / "tabs" / "webhook_monitor.py"
    if webhook_file.exists():
        results = find_st_metric_in_file(webhook_file)
        # Hata durumlarini sayma
        actual_errors = [r for r in results if "error" not in r]
        assert len(actual_errors) == 0, f"webhook_monitor.py hala {len(actual_errors)} st.metric iceriyor: {actual_errors}"


def test_tenant_health_dashboard_no_st_metric():
    """tenant_health_dashboard.py dosyasinda `st.metric` yokmalidir (ADMIN-KPI-KART-02 sonrasi)."""
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[1]
    tenant_file = ROOT / "web_dashboard" / "tabs" / "tenant_health_dashboard.py"
    if tenant_file.exists():
        results = find_st_metric_in_file(tenant_file)
        actual_errors = [r for r in results if "error" not in r]
        assert len(actual_errors) == 0, f"tenant_health_dashboard.py hala {len(actual_errors)} st.metric iceriyor: {actual_errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
