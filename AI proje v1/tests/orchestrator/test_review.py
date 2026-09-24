"""Tests for orchestrator review gate."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from src.company_master.orchestrator.models import TaskType
from src.company_master.orchestrator.review import ReviewError, review_output
from src.company_master.orchestrator.workspace import resolve_workspace


def _agent_output_dir(agent_id: str, tmp_path: Path, name: str) -> Path:
    allowed = resolve_workspace(agent_id)
    test_dir = allowed / "test_runs" / name
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


def test_review_clean_output(tmp_path):
    agent_id = "cursor_grok"
    out_dir = _agent_output_dir(agent_id, tmp_path, "review_clean")
    (out_dir / "output.txt").write_text("hello world\n", encoding="utf-8")
    result = review_output(agent_id, out_dir, ["output.txt"])
    assert result.success is True
    assert result.metrics["secret_hits"] == 0


def test_review_secret_detected(tmp_path):
    agent_id = "cursor_grok"
    out_dir = _agent_output_dir(agent_id, tmp_path, "review_secret")
    (out_dir / "leak.py").write_text("API_KEY = 'secret123'\n", encoding="utf-8")
    result = review_output(agent_id, out_dir, ["leak.py"])
    assert result.success is False
    assert result.metrics["secret_hits"] >= 1


def test_review_missing_file(tmp_path):
    agent_id = "cursor_grok"
    out_dir = _agent_output_dir(agent_id, tmp_path, "review_missing")
    result = review_output(agent_id, out_dir, ["file:missing.txt"])
    assert result.success is False
    assert any("missing.txt" in f for f in result.findings)


def test_review_nonexistent_path():
    with pytest.raises(ReviewError):
        review_output("cursor_grok", "/nonexistent/path", [])
