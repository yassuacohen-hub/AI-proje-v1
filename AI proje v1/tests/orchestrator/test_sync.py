"""Tests for orchestrator sync module."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from src.company_master.orchestrator.models import TaskResult
from src.company_master.orchestrator.sync import SyncError, append_completion, update_error_ledger_section


def test_append_completion(tmp_path):
    agent_sync = tmp_path / "AGENT_SYNC.md"
    agent_sync.write_text(
        "# AGENT_SYNC\n\n## Tamamlananlar (Senkron Kaydi)\n\n| Ajan | Tarih | Yapilan Is |\n|------|-------|------------|\n",
        encoding="utf-8",
    )
    import src.company_master.orchestrator.sync as sync_mod
    original = sync_mod.AGENT_SYNC_PATH
    sync_mod.AGENT_SYNC_PATH = agent_sync
    try:
        result = TaskResult(success=True, summary="test summary")
        append_completion("Kilo Code", "TSK-001", "did work", result)
        content = agent_sync.read_text(encoding="utf-8")
        assert "TSK-001" in content
        assert "test summary" in content
    finally:
        sync_mod.AGENT_SYNC_PATH = original


def test_update_error_ledger_section(tmp_path):
    agent_sync = tmp_path / "AGENT_SYNC.md"
    agent_sync.write_text("# AGENT_SYNC\n\n## ErrorLedger\n\nold\n", encoding="utf-8")
    import src.company_master.orchestrator.sync as sync_mod
    original = sync_mod.AGENT_SYNC_PATH
    sync_mod.AGENT_SYNC_PATH = agent_sync
    try:
        entries = [
            {
                "task_id": "TSK-1",
                "agent_id": "cursor_grok",
                "timestamp": "2026-09-03T00:00:00",
                "error_type": "timeout",
                "error_message": "timed out",
                "attempt": 1,
                "action": "retry",
            }
        ]
        update_error_ledger_section(entries)
        content = agent_sync.read_text(encoding="utf-8")
        assert "TSK-1" in content
        assert "timeout" in content
    finally:
        sync_mod.AGENT_SYNC_PATH = original


def test_append_completion_missing_file(tmp_path):
    import src.company_master.orchestrator.sync as sync_mod
    original = sync_mod.AGENT_SYNC_PATH
    sync_mod.AGENT_SYNC_PATH = tmp_path / "missing.md"
    try:
        with pytest.raises(SyncError):
            append_completion("X", "TSK-1", "y")
    finally:
        sync_mod.AGENT_SYNC_PATH = original
