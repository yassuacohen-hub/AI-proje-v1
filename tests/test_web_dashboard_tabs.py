"""Unit tests for web dashboard tab helpers."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from web_dashboard.tabs import (
    admin_audit,
    admin_auth,
    admin_dlq,
    admin_kpi,
    admin_panel,
    admin_performance,
    webhook_monitor,
)


def test_admin_auth_reads_token_and_reports_missing_token(monkeypatch):
    monkeypatch.setattr(admin_auth.st, "session_state", {"admin_token": "secret"})
    assert admin_auth.get_admin_token() == "secret"
    assert admin_auth.require_admin_token() == "secret"

    monkeypatch.setattr(admin_auth.st, "session_state", {})
    admin_auth.st.info = MagicMock()
    assert admin_auth.require_admin_token() is None
    admin_auth.st.info.assert_called_once()


@pytest.fixture
def form_durumu_geri():
    """`render_decision_tab` bare modda `st.form("yeni_karar")` cagirir.

    ScriptRunContext yokken form blogu main_dg'nin kendisidir ve `with`
    cikisi `_form_data`yi temizlemez; kalinti sonraki `AppTest` kosusunda
    "Forms cannot be nested in other forms." olur (D-226).
    Mandal: tests/conftest.py::_streamlit_form_durumu_temiz.
    """
    yield
    from streamlit.delta_generator_singletons import get_dg_singleton_instance

    get_dg_singleton_instance().main_dg._form_data = None


def test_decision_tab_handles_empty_and_limits_recent_rows(monkeypatch, form_durumu_geri):
    admin_panel.st.info = MagicMock()
    admin_panel.render_decision_tab([])
    admin_panel.st.info.assert_called_once()

    # MVP-KD-01: kayitlar ts'e gore YENIDEN ESKIYE siralanir, ilk 50 gosterilir.
    decisions = [
        {"ts": f"2026-01-01T00:00:{index:02d}", "title": f"Karar {index}", "tags": ["test"]}
        for index in range(55)
    ]
    dataframe = MagicMock()
    monkeypatch.setattr(admin_panel.st, "dataframe", dataframe)
    admin_panel.render_decision_tab(decisions)

    rendered_rows = dataframe.call_args.args[0]
    assert len(rendered_rows) == 50
    assert rendered_rows.iloc[0]["Baslik"] == "Karar 54"
    assert rendered_rows.iloc[-1]["Baslik"] == "Karar 5"


def test_webhook_helpers_cover_statuses_and_timestamps():
    assert webhook_monitor._status_color("SUCCEEDED") == "🟢"
    assert webhook_monitor._status_color("FAILED") == "🔴"
    assert webhook_monitor._status_color("unknown") == "⚪"
    assert webhook_monitor._format_ts(None) == "—"
    assert webhook_monitor._format_ts("2026-09-13T12:34:56.000Z") == "2026-09-13T12:34:56"


def test_load_webhook_stats_ignores_invalid_jsonl(monkeypatch, tmp_path: Path):
    events = tmp_path / "events.jsonl"
    events.write_text(
        '{"status":"SUCCEEDED","triggered_at":"2026-09-13T10:00:00Z"}\n'
        '{invalid json}\n'
        '{"status":"FAILED"}\n',
        encoding="utf-8",
    )
    dlq = tmp_path / "dlq.jsonl"
    dlq.write_text('{"error_type":"timeout"}\n', encoding="utf-8")
    monkeypatch.setattr(webhook_monitor, "WEBHOOK_EVENTS", events)
    monkeypatch.setattr(webhook_monitor, "WEBHOOK_DLQ", dlq)
    webhook_monitor.load_webhook_stats.clear()

    stats = webhook_monitor.load_webhook_stats()

    assert stats["olay_toplam"] == 2
    assert stats["basarili"] == 1
    assert stats["hatali"] == 1
    assert stats["dlq_toplam"] == 1
    assert stats["hata_turleri"] == {"timeout": 1}


def test_audit_loaders_return_valid_entries_only(monkeypatch, tmp_path: Path):
    locks = tmp_path / "locks.json"
    locks.write_text('{"file.py":{"sahip":"copilot"}}', encoding="utf-8")
    handoffs = tmp_path / "handoffs.json"
    handoffs.write_text('{"COP-02":{"tamamlandi":"tests"}}', encoding="utf-8")
    triggers = tmp_path / "triggers.jsonl"
    triggers.write_text('{"task_id":"COP-02"}\ninvalid\n', encoding="utf-8")
    monkeypatch.setattr(admin_audit, "FILE_LOCKS", locks)
    monkeypatch.setattr(admin_audit, "HANDOFFS", handoffs)
    monkeypatch.setattr(admin_audit, "TRIGGER_LOG", triggers)
    admin_audit.load_file_locks.clear()
    admin_audit.load_handoffs.clear()
    admin_audit.load_trigger_log.clear()

    assert admin_audit.load_file_locks()["file.py"]["sahip"] == "copilot"
    assert admin_audit.load_handoffs()["COP-02"]["tamamlandi"] == "tests"
    assert admin_audit.load_trigger_log() == [{"task_id": "COP-02"}]


def test_kpi_task_summary_counts_statuses(monkeypatch):
    monkeypatch.setattr(
        "company_master.orchestrator.task_board.gorev_listesi",
        lambda: [
            {"durum": "done"},
            {"durum": "aktif"},
            {"durum": "blocked"},
            {"durum": "unknown"},
        ],
    )
    admin_kpi.load_task_summary.clear()

    summary = admin_kpi.load_task_summary()

    assert summary["toplam"] == 4
    assert summary["done"] == 1
    assert summary["aktif"] == 1
    assert summary["blocked"] == 1
    assert summary["review"] == 0


def test_kpi_renders_spinner_placeholder_when_data_missing(monkeypatch):
    monkeypatch.setattr(admin_kpi, "load_admin_kpi_summary", lambda: {})

    class DummySpinner:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    spinner = MagicMock(return_value=DummySpinner())
    monkeypatch.setattr(admin_kpi.st, "spinner", spinner)
    monkeypatch.setattr(admin_kpi.st, "subheader", MagicMock())
    monkeypatch.setattr(admin_kpi.st, "caption", MagicMock())
    monkeypatch.setattr(admin_kpi.st, "divider", MagicMock())
    monkeypatch.setattr(admin_kpi.st, "columns", lambda n: [MagicMock() for _ in range(n)])

    admin_kpi.render_kpi_tab()

    spinner.assert_called_once_with("Veri yukleniyor...")


def test_dlq_tab_handles_empty_and_populated_data(monkeypatch):
    monkeypatch.setattr(
        admin_dlq,
        "load_dlq_stats",
        lambda: {"dlq_toplam": 0, "hata_turleri": {}, "entries": []},
    )
    success = MagicMock()
    monkeypatch.setattr(admin_dlq.st, "success", success)
    admin_dlq.render_dlq_tab()
    success.assert_called_once_with("DLQ boş — aktif hata kuyruğu yok.")

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
    monkeypatch.setattr(admin_dlq.st, "button", lambda label: False)
    monkeypatch.setattr(admin_dlq.st, "subheader", MagicMock())
    monkeypatch.setattr(admin_dlq.st, "divider", MagicMock())
    monkeypatch.setattr(admin_dlq.st, "caption", MagicMock())

    admin_dlq.render_dlq_tab()

    assert metric.called
    assert bar.called
    assert dataframe.called


def test_performance_loaders_and_empty_render(monkeypatch):
    monkeypatch.setattr(
        admin_performance,
        "get_api",
        lambda endpoint: {
            "db_time_ms": 120,
            "query_count": 4,
        },
    )
    admin_performance.load_performance_data.clear()
    assert admin_performance.load_performance_data() == {
        "db_time_ms": 120,
        "query_count": 4,
    }

    admin_performance.load_prometheus_metrics.clear()
    monkeypatch.setattr(admin_performance, "load_prometheus_metrics", lambda: {})
    monkeypatch.setattr(admin_performance, "load_performance_data", lambda: {})
    info = MagicMock()
    monkeypatch.setattr(admin_performance.st, "info", info)

    admin_performance.render_performance_tab()

    info.assert_called_once_with("Performans verisi yüklenemedi.")

