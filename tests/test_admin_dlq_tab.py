from unittest.mock import MagicMock

from web_dashboard.tabs import admin_dlq


def test_render_dlq_tab_empty_state(monkeypatch):
    monkeypatch.setattr(
        admin_dlq,
        "load_dlq_stats",
        lambda: {"dlq_toplam": 0, "hata_turleri": {}, "entries": []},
    )
    success = MagicMock()
    monkeypatch.setattr(admin_dlq.st, "success", success)
    monkeypatch.setattr(admin_dlq.st, "subheader", MagicMock())
    monkeypatch.setattr(admin_dlq.st, "divider", MagicMock())
    monkeypatch.setattr(admin_dlq.st, "columns", lambda n: [MagicMock() for _ in range(n)])

    admin_dlq.render_dlq_tab()

    success.assert_called_once_with("DLQ boş — aktif hata kuyruğu yok.")


def test_render_dlq_tab_with_data(monkeypatch):
    monkeypatch.setattr(
        admin_dlq,
        "load_dlq_stats",
        lambda: {
            "dlq_toplam": 2,
            "retryable": 1,
            "non_retryable": 1,
            "ortalama_yas_saat": 2.5,
            "hata_turleri": {"timeout": 2},
            "entries": [{"timestamp": "2026-09-13T12:00:00", "error_type": "timeout", "error": "timeout"}],
            "en_eski": "2026-09-13T11:00:00",
            "en_yeni": "2026-09-13T12:00:00",
        },
    )
    metric = MagicMock()
    bar = MagicMock()
    dataframe = MagicMock()
    monkeypatch.setattr(admin_dlq, "kpi_karti", metric)
    monkeypatch.setattr(admin_dlq.st, "bar_chart", bar)
    monkeypatch.setattr(admin_dlq.st, "dataframe", dataframe)
    monkeypatch.setattr(admin_dlq.st, "info", MagicMock())
    monkeypatch.setattr(admin_dlq.st, "button", lambda *args, **kwargs: False)
    monkeypatch.setattr(admin_dlq.st, "subheader", MagicMock())
    monkeypatch.setattr(admin_dlq.st, "divider", MagicMock())
    monkeypatch.setattr(admin_dlq.st, "caption", MagicMock())

    admin_dlq.render_dlq_tab()

    assert metric.called
    assert bar.called
    assert dataframe.called
