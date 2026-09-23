from unittest.mock import MagicMock

from web_dashboard.tabs import webhook_monitor


def test_render_webhook_monitor_tab_handles_empty_and_populated_data(monkeypatch):
    monkeypatch.setattr(webhook_monitor, "load_health_check", lambda: {})
    monkeypatch.setattr(
        webhook_monitor,
        "load_webhook_stats",
        lambda: {"olay_toplam": 0, "basarili": 0, "hatali": 0, "calisan": 0, "dlq_toplam": 0, "hata_turleri": {}, "olaylar": [], "dlq_girdileri": [], "son_olay": None},
    )
    monkeypatch.setattr(webhook_monitor, "load_prometheus_metrics", lambda: {})

    info = MagicMock()
    monkeypatch.setattr(webhook_monitor.st, "info", info)
    monkeypatch.setattr(webhook_monitor.st, "subheader", MagicMock())
    monkeypatch.setattr(webhook_monitor.st, "caption", MagicMock())
    monkeypatch.setattr(webhook_monitor.st, "divider", MagicMock())
    monkeypatch.setattr(
        webhook_monitor.st,
        "columns",
        lambda n: [MagicMock() for _ in range(len(n) if isinstance(n, list) else n)],
    )

    webhook_monitor.render_webhook_monitor_tab()

    info.assert_any_call("Health check verisi yüklenemedi.")
    info.assert_any_call("Henüz webhook olay kaydı bulunmuyor.")
    info.assert_any_call("DLQ boş — hatalı olay kaydı yok.")


def test_render_webhook_monitor_tab_renders_metrics(monkeypatch):
    monkeypatch.setattr(webhook_monitor, "load_health_check", lambda: {"status": "healthy", "secret_configured": True, "rate_limit_enabled": True, "dlq_size": 2, "processed_runs_memory": 3, "prometheus_available": True})
    monkeypatch.setattr(
        webhook_monitor,
        "load_webhook_stats",
        lambda: {
            "olay_toplam": 2,
            "basarili": 1,
            "hatali": 1,
            "calisan": 0,
            "dlq_toplam": 1,
            "hata_turleri": {"timeout": 1},
            "olaylar": [{"status": "SUCCEEDED"}, {"status": "FAILED"}],
            "dlq_girdileri": [{"error_type": "timeout", "timestamp": "2026-09-13T12:00:00", "reason": "network"}],
            "son_olay": "2026-09-13T12:00:00",
        },
    )
    monkeypatch.setattr(webhook_monitor, "load_prometheus_metrics", lambda: {"apify_webhook_duration_seconds": "0.23"})

    success = MagicMock()
    kpi = MagicMock()
    bar = MagicMock()
    dataframe = MagicMock()
    monkeypatch.setattr(webhook_monitor.st, "success", success)
    monkeypatch.setattr(webhook_monitor, "kpi_karti", kpi)
    monkeypatch.setattr(webhook_monitor.st, "bar_chart", bar)
    monkeypatch.setattr(webhook_monitor.st, "dataframe", dataframe)
    monkeypatch.setattr(webhook_monitor.st, "subheader", MagicMock())
    monkeypatch.setattr(webhook_monitor.st, "caption", MagicMock())
    monkeypatch.setattr(webhook_monitor.st, "divider", MagicMock())
    monkeypatch.setattr(
        webhook_monitor.st,
        "columns",
        lambda n: [MagicMock() for _ in range(len(n) if isinstance(n, list) else n)],
    )

    webhook_monitor.render_webhook_monitor_tab()

    assert kpi.called
    assert bar.called
    assert dataframe.called
