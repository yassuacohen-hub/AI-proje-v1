"""Tests for orchestrator workspace isolation."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from src.company_master.orchestrator.models import AgentManifest, TaskType
from src.company_master.orchestrator.workspace import (
    WorkspaceViolation,
    enforce_isolation,
    resolve_workspace,
    scan_for_secrets,
    validate_manifest,
    validate_write_path,
)


def test_resolve_workspace():
    path = resolve_workspace("cursor_grok")
    assert path.parts[-2:] == ("external", "cursor_grok")


def test_validate_write_path_inside_workspace():
    path = validate_write_path("cursor_grok", "workspace/external/cursor_grok/output/review.md")
    assert path.name == "review.md"
    assert "cursor_grok" in path.parts


def test_validate_write_path_outside_workspace():
    with pytest.raises(WorkspaceViolation):
        validate_write_path("cursor_grok", "src/company_master/db/connection.py")


def test_validate_manifest_valid():
    manifest = AgentManifest(
        agent_id="copilot",
        display_name="Copilot",
        task_type=TaskType.REFACTORING,
        workspace_path="workspace/external/copilot",
    )
    validate_manifest(manifest)


def test_validate_manifest_invalid_workspace():
    manifest = AgentManifest(
        agent_id="evil",
        display_name="Evil",
        task_type=TaskType.REFACTORING,
        workspace_path="src/company_master/orchestrator",
    )
    with pytest.raises(WorkspaceViolation):
        validate_manifest(manifest)


def test_scan_for_secrets_clean(tmp_path):
    clean = tmp_path / "clean.py"
    clean.write_text("x = 1\n", encoding="utf-8")
    assert scan_for_secrets(clean) == []


def test_scan_for_secrets_detected(tmp_path):
    dirty = tmp_path / "secret.py"
    dirty.write_text("API_KEY = 'secret123'\n", encoding="utf-8")
    findings = scan_for_secrets(dirty)
    assert len(findings) == 1
    assert "secret.py" in findings[0]
