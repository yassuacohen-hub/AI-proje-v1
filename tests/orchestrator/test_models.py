"""Tests for orchestrator models."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from src.company_master.orchestrator.models import (
    AgentManifest,
    Brief,
    ErrorLedgerEntry,
    Task,
    TaskResult,
    TaskStatus,
    TaskType,
)


def test_task_status_values():
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.COMPLETED.value == "completed"


def test_task_type_values():
    assert TaskType.CODE_REVIEW.value == "code_review"
    assert TaskType.RESEARCH.value == "research"


def test_task_roundtrip():
    task = Task(
        task_id="TSK-001",
        agent_id="cursor_grok",
        task_type=TaskType.CODE_REVIEW,
        brief_path="workspace/external/cursor_grok/brief.md",
        status=TaskStatus.COMPLETED,
    )
    data = task.to_dict()
    restored = Task.from_dict(data)
    assert restored.task_id == "TSK-001"
    assert restored.status == TaskStatus.COMPLETED


def test_task_result_roundtrip():
    result = TaskResult(success=True, summary="done", findings=["ok"])
    data = result.to_dict()
    restored = TaskResult.from_dict(data)
    assert restored.success is True
    assert restored.findings == ["ok"]


def test_error_ledger_entry_roundtrip():
    entry = ErrorLedgerEntry(
        task_id="TSK-001",
        agent_id="cursor_grok",
        error_type="timeout",
        attempt=2,
        action="reassign",
    )
    data = entry.to_dict()
    restored = ErrorLedgerEntry.from_dict(data)
    assert restored.error_type == "timeout"
    assert restored.action == "reassign"


def test_agent_manifest_roundtrip():
    manifest = AgentManifest(
        agent_id="copilot",
        display_name="GitHub Copilot",
        task_type=TaskType.REFACTORING,
        workspace_path="workspace/external/copilot",
        max_attempts=3,
    )
    data = manifest.to_dict()
    restored = AgentManifest.from_dict(data)
    assert restored.agent_id == "copilot"
    assert restored.max_attempts == 3


def test_brief_roundtrip():
    brief = Brief(
        agent_id="claude_code",
        task_id="TSK-002",
        task_type=TaskType.RESEARCH,
        title="Research task",
        brief_path="workspace/external/claude_code/brief.md",
    )
    data = brief.to_dict()
    restored = Brief.from_dict(data)
    assert restored.task_id == "TSK-002"
    assert restored.title == "Research task"
