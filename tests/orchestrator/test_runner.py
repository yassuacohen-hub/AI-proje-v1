"""Tests for orchestrator runner."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from src.company_master.orchestrator.models import (
    AgentManifest,
    ErrorLedgerEntry,
    Task,
    TaskStatus,
    TaskType,
)
from src.company_master.orchestrator.runner import TaskExecutionError, run_task


def _make_task(task_id: str = "TSK-001") -> Task:
    return Task(
        task_id=task_id,
        agent_id="cursor_grok",
        task_type=TaskType.CODE_REVIEW,
        brief_path="workspace/external/cursor_grok/brief.md",
        status=TaskStatus.PENDING,
    )


def _make_manifest() -> AgentManifest:
    return AgentManifest(
        agent_id="cursor_grok",
        display_name="Cursor Grok",
        task_type=TaskType.CODE_REVIEW,
        workspace_path="workspace/external/cursor_grok",
        max_attempts=2,
        timeout_seconds=1,
        retry_backoff_seconds=0,
    )


def test_run_task_success(tmp_path):
    manifest = _make_manifest()
    manifest.timeout_seconds = 10
    manifest.workspace_path = str(tmp_path)
    (tmp_path / "run.py").write_text("import sys; sys.exit(0)\n", encoding="utf-8")
    task = _make_task()
    ledger: list[ErrorLedgerEntry] = []
    completed, result = run_task(task, manifest, ledger)
    assert completed.status == TaskStatus.COMPLETED
    assert result.success is True


def test_run_task_failure_then_reassign(tmp_path):
    manifest = _make_manifest()
    manifest.max_attempts = 2
    manifest.timeout_seconds = 10
    manifest.workspace_path = str(tmp_path)
    (tmp_path / "run.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")
    task = _make_task()
    ledger: list[ErrorLedgerEntry] = []
    completed, result = run_task(task, manifest, ledger)
    assert completed.status == TaskStatus.REASSIGNED
    assert len(ledger) == 2
    assert ledger[0].action == "retry"
    assert ledger[1].action == "reassign"
