from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from web_dashboard.tabs import admin_audit


def test_render_audit_tab_handles_missing_locks(monkeypatch):
    monkeypatch.setattr(admin_audit, "read_decisions", lambda limit=30: [])
    monkeypatch.setattr(admin_audit, "load_file_locks", lambda: {})
    monkeypatch.setattr(admin_audit, "load_handoffs", lambda: {})
    monkeypatch.setattr(admin_audit, "load_trigger_log", lambda: [])
    monkeypatch.setattr(
        admin_audit.tb,
        "gorev_listesi",
        lambda: [{"task_id": "COP-01", "baslik": "Test", "sahip": "copilot", "oncelik": "P1", "durum": "done"}],
    )

    for name in ["subheader", "caption", "divider", "info", "success", "dataframe", "metric"]:
        setattr(admin_audit.st, name, MagicMock())

    monkeypatch.setattr(admin_audit.st, "columns", lambda n: [MagicMock() for _ in range(n)])

    admin_audit.render_audit_tab()

    admin_audit.st.success.assert_any_call("✅ Aktif dosya kilidi yok — tüm dosyalar serbest.")


def test_render_audit_tab_handles_present_locks(monkeypatch):
    monkeypatch.setattr(admin_audit, "read_decisions", lambda limit=30: [])
    monkeypatch.setattr(
        admin_audit,
        "load_file_locks",
        lambda: {"/tmp/file.py": {"sahip": "copilot", "task_id": "COP-02", "kilitlendi": "2026-09-13T12:00:00Z"}},
    )
    monkeypatch.setattr(admin_audit, "load_handoffs", lambda: {})
    monkeypatch.setattr(admin_audit, "load_trigger_log", lambda: [])
    monkeypatch.setattr(admin_audit.tb, "gorev_listesi", lambda: [])

    for name in ["subheader", "caption", "divider", "info", "success", "dataframe", "metric"]:
        setattr(admin_audit.st, name, MagicMock())

    admin_audit.render_audit_tab()

    assert admin_audit.st.dataframe.called


def test_load_file_locks_ignores_invalid_json(monkeypatch, tmp_path: Path):
    bad_file = tmp_path / "file_locks.json"
    bad_file.write_text('{"broken": ', encoding="utf-8")
    monkeypatch.setattr(admin_audit, "FILE_LOCKS", bad_file)
    admin_audit.load_file_locks.clear()

    assert admin_audit.load_file_locks() == {}
