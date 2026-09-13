from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from scripts import decision_log
from web_dashboard.tabs import admin_panel


def test_render_decision_tab_shows_empty_state(monkeypatch):
    info = MagicMock()
    monkeypatch.setattr(admin_panel.st, "info", info)

    admin_panel.render_decision_tab([])

    info.assert_called_once_with("Henüz karar kaydı yok")


def test_render_decision_tab_renders_populated_log(monkeypatch):
    dataframe = MagicMock()
    caption = MagicMock()
    monkeypatch.setattr(admin_panel.st, "dataframe", dataframe)
    monkeypatch.setattr(admin_panel.st, "caption", caption)

    decisions = [
        {
            "ts": "2026-09-13T12:00:00+00:00",
            "title": "Test kararı",
            "decision": "accepted",
            "decider": "copilot",
            "reason": "Test gerekçesi",
            "tags": ["test", "audit"],
        }
    ]

    admin_panel.render_decision_tab(decisions)

    rendered = dataframe.call_args.args[0]
    assert len(rendered) == 1
    assert rendered.iloc[0]["Baslik"] == "Test kararı"
    assert rendered.iloc[0]["Etiketler"] == "test, audit"
    caption.assert_called_once()


def test_read_decisions_skips_broken_jsonl_lines(monkeypatch, tmp_path: Path):
    log_file = tmp_path / "decision_log.jsonl"
    log_file.write_text(
        '{"title":"gecerli","decision":"accepted"}\n'
        '{bozuk jsonl}\n'
        '{"title":"ikinci","decision":"deferred"}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(decision_log, "DECISION_LOG", log_file)

    entries = decision_log.read_decisions()

    assert [entry["title"] for entry in entries] == ["gecerli", "ikinci"]
