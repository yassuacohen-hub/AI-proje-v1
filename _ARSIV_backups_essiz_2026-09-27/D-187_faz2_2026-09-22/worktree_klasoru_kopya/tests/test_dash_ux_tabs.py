# -*- coding: utf-8 -*-
"""DASH-UX-02a.v1: admin_sistem.py testleri."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# src yolunu ekle
_KOK = Path(__file__).resolve().parents[1]
if str(_KOK / "src") not in sys.path:
    sys.path.insert(0, str(_KOK / "src"))


def test_admin_sistem_import() -> None:
    """Modül import edilebilir."""
    from web_dashboard.tabs import admin_sistem

    assert hasattr(admin_sistem, "render_admin_sistem")
    assert hasattr(admin_sistem, "_render_cost_tab")
    assert hasattr(admin_sistem, "_render_performance_tab")
    assert hasattr(admin_sistem, "_render_api_analytics_tab")
    assert hasattr(admin_sistem, "_render_dlq_tab")
    assert hasattr(admin_sistem, "_render_webhook_tab")


def test_render_admin_sistem_cagrisi(monkeypatch) -> None:
    """render_admin_sistem 5 alt sekme fonksiyonunu çağırır."""
    import web_dashboard.tabs.admin_sistem as mod

    mock_st = MagicMock()
    mock_tabs = MagicMock()
    mock_context_managers = [MagicMock() for _ in range(5)]
    for i, cm in enumerate(mock_context_managers):
        cm.__enter__ = MagicMock(return_value=None)
        cm.__exit__ = MagicMock(return_value=None)
    mock_tabs.__getitem__ = MagicMock(side_effect=lambda x: mock_context_managers[x])
    mock_st.tabs = MagicMock(return_value=mock_tabs)
    mock_st.header = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.columns = MagicMock(side_effect=lambda n: [MagicMock() for _ in range(n)])

    mock_render_cost = MagicMock()
    mock_render_perf = MagicMock()
    mock_render_api = MagicMock()
    mock_render_dlq = MagicMock()
    mock_render_webhook = MagicMock()

    monkeypatch.setattr("streamlit.header", mock_st.header)
    monkeypatch.setattr("streamlit.tabs", mock_st.tabs)
    monkeypatch.setattr("streamlit.caption", mock_st.caption)
    monkeypatch.setattr("streamlit.columns", mock_st.columns)
    monkeypatch.setattr(mod, "_render_cost_tab", mock_render_cost)
    monkeypatch.setattr(mod, "_render_performance_tab", mock_render_perf)
    monkeypatch.setattr(mod, "_render_api_analytics_tab", mock_render_api)
    monkeypatch.setattr(mod, "_render_dlq_tab", mock_render_dlq)
    monkeypatch.setattr(mod, "_render_webhook_tab", mock_render_webhook)

    mod.render_admin_sistem()

    mock_st.header.assert_called_once_with("⚙️ Sistem Yönetimi")
    mock_st.tabs.assert_called_once()
    assert mock_render_cost.call_count == 1
    assert mock_render_perf.call_count == 1
    assert mock_render_api.call_count == 1
    assert mock_render_dlq.call_count == 1
    assert mock_render_webhook.call_count == 1


def test_render_cost_tab_veri_yok(monkeypatch) -> None:
    """Cost sekmesi veri yoksa info gösterir."""
    from web_dashboard.tabs.admin_sistem import _render_cost_tab

    mock_st = MagicMock()
    mock_load = MagicMock(return_value=MagicMock(provider_count=0))
    mock_button = MagicMock()
    mock_st.info = MagicMock()
    mock_st.button = mock_button
    mock_st.code = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.columns = MagicMock(side_effect=lambda n: [MagicMock() for _ in range(n)])

    monkeypatch.setattr("streamlit.info", mock_st.info)
    monkeypatch.setattr("streamlit.button", mock_button)
    monkeypatch.setattr("streamlit.code", mock_st.code)
    monkeypatch.setattr("streamlit.subheader", mock_st.subheader)
    monkeypatch.setattr("streamlit.divider", mock_st.divider)
    monkeypatch.setattr("streamlit.columns", mock_st.columns)
    monkeypatch.setattr("web_dashboard.tabs.admin_sistem.load_cost_summary", mock_load)

    _render_cost_tab()

    mock_st.info.assert_called()
    mock_load.assert_called_once()


def test_render_performance_tab_veri_yok(monkeypatch) -> None:
    """Performance sekmesi veri yoksa info gösterir."""
    from web_dashboard.tabs.admin_sistem import _render_performance_tab

    mock_st = MagicMock()
    mock_load_perf = MagicMock(return_value={})
    mock_load_ai = MagicMock(return_value={"toplam_cagri": 0})
    mock_st.info = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.columns = MagicMock(side_effect=lambda n: [MagicMock() for _ in range(n)])

    monkeypatch.setattr("streamlit.info", mock_st.info)
    monkeypatch.setattr("streamlit.subheader", mock_st.subheader)
    monkeypatch.setattr("streamlit.markdown", mock_st.markdown)
    monkeypatch.setattr("streamlit.divider", mock_st.divider)
    monkeypatch.setattr("streamlit.columns", mock_st.columns)
    monkeypatch.setattr("web_dashboard.tabs.admin_sistem.load_performance_data", mock_load_perf)
    monkeypatch.setattr("web_dashboard.tabs.admin_sistem.load_ai_cost_per_call", mock_load_ai)
    monkeypatch.setattr("web_dashboard.charts.kpi_karti", MagicMock())

    _render_performance_tab()

    mock_st.info.assert_called()


def test_render_dlq_tab_bos(monkeypatch) -> None:
    """DLQ sekmesi boşsa success gösterir."""
    from web_dashboard.tabs.admin_sistem import _render_dlq_tab

    mock_st = MagicMock()
    mock_load = MagicMock(return_value={"dlq_toplam": 0, "retryable": 0, "non_retryable": 0,
                                         "ortalama_yas_saat": 0, "en_eski": None, "en_yeni": None,
                                         "hata_turleri": {}, "entries": []})
    mock_st.success = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.columns = MagicMock(side_effect=lambda n: [MagicMock() for _ in range(n)])
    mock_st.markdown = MagicMock()

    monkeypatch.setattr("streamlit.success", mock_st.success)
    monkeypatch.setattr("streamlit.subheader", mock_st.subheader)
    monkeypatch.setattr("streamlit.divider", mock_st.divider)
    monkeypatch.setattr("streamlit.columns", mock_st.columns)
    monkeypatch.setattr("streamlit.markdown", mock_st.markdown)
    monkeypatch.setattr("web_dashboard.tabs.admin_sistem.load_dlq_stats", mock_load)

    _render_dlq_tab()

    mock_st.success.assert_called_once()


def test_render_webhook_tab_health_yok(monkeypatch) -> None:
    """Webhook sekmesi health check yoksa info gösterir."""
    from web_dashboard.tabs.admin_sistem import _render_webhook_tab

    mock_st = MagicMock()
    mock_load_health = MagicMock(return_value={})
    mock_load_stats = MagicMock(return_value={"olay_toplam": 0, "basarili": 0, "hatali": 0,
                                               "calisan": 0, "son_olay": None, "dlq_toplam": 0,
                                               "hata_turleri": {}, "olaylar": [], "dlq_girdileri": []})
    mock_load_prom = MagicMock(return_value={})
    mock_st.info = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.columns = MagicMock(side_effect=lambda n: [MagicMock() for _ in range(n)])

    monkeypatch.setattr("streamlit.info", mock_st.info)
    monkeypatch.setattr("streamlit.subheader", mock_st.subheader)
    monkeypatch.setattr("streamlit.divider", mock_st.divider)
    monkeypatch.setattr("streamlit.caption", mock_st.caption)
    monkeypatch.setattr("streamlit.columns", mock_st.columns)
    monkeypatch.setattr("web_dashboard.tabs.admin_sistem.load_health_check", mock_load_health)
    monkeypatch.setattr("web_dashboard.tabs.admin_sistem.load_webhook_stats", mock_load_stats)
    monkeypatch.setattr("web_dashboard.tabs.admin_sistem.load_webhook_prometheus_metrics", mock_load_prom)
    monkeypatch.setattr("web_dashboard.charts.kpi_karti", MagicMock())

    _render_webhook_tab()

    mock_st.info.assert_called()


def test_k1_kalibrasyonu_tanimli() -> None:
    """K1 kalibrasyonu dosyada tanımlı mı (docstring kontrolü)."""
    import web_dashboard.tabs.admin_sistem as mod
    import inspect

    source = inspect.getsource(mod.render_admin_sistem)
    assert "K1" in source
    assert "st.tabs" in source
    assert "cache" in source.lower() or "ttl" in source.lower()


def test_veri_kaynaklari_import_edilebilir() -> None:
    """5 veri kaynağı modülünden import edilebilir."""
    from web_dashboard.tabs.admin_cost import load_cost_summary
    from web_dashboard.tabs.admin_performance import load_performance_data, load_ai_cost_per_call
    from web_dashboard.tabs.admin_api_analytics import load_api_usage, load_metrics_summary
    from web_dashboard.tabs.admin_dlq import load_dlq_stats
    from web_dashboard.tabs.webhook_monitor import load_webhook_stats, load_health_check

    assert callable(load_cost_summary)
    assert callable(load_performance_data)
    assert callable(load_ai_cost_per_call)
    assert callable(load_api_usage)
    assert callable(load_metrics_summary)
    assert callable(load_dlq_stats)
    assert callable(load_webhook_stats)
    assert callable(load_health_check)


def test_kpi_kategori_dogru() -> None:
    """KPI kartları doğru kategori parametresiyle çağrılır (kod incelemesi)."""
    import web_dashboard.tabs.admin_sistem as mod
    import inspect

    source = inspect.getsource(mod)
    # Cost sekmesi "maliyet" kategorisi
    assert 'kategori="maliyet"' in source
    # Performance/System "sistem" kategorisi
    assert 'kategori="sistem"' in source
    # DLQ "uyari" kategorisi
    assert 'kategori="uyari"' in source
    # Webhook "bilgi"/"basari"/"hata" kategorileri
    assert 'kategori="bilgi"' in source or 'kategori="basari"' in source or 'kategori="hata"' in source