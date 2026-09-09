"""Tests for orchestrator brief packaging."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from src.company_master.orchestrator.brief import BriefValidationError, load_brief, package_brief
from src.company_master.orchestrator.models import Brief, TaskType


def test_load_brief_json(tmp_path):
    brief_data = {
        "agent_id": "cursor_grok",
        "task_id": "TSK-001",
        "task_type": "code_review",
        "title": "Review app.py",
        "success_criteria": ["file:app.py.optimized"],
    }
    p = tmp_path / "brief.json"
    p.write_text(json.dumps(brief_data), encoding="utf-8")
    loaded = load_brief(p)
    assert loaded.task_id == "TSK-001"
    assert loaded.agent_id == "cursor_grok"


def test_load_brief_markdown(tmp_path):
    content = """{
  "agent_id": "cursor_grok",
  "task_id": "TSK-002",
  "task_type": "code_review",
  "title": "Review scraper",
  "success_criteria": ["file:review.md"]
}
"""
    p = tmp_path / "brief.json"
    p.write_text(content, encoding="utf-8")
    loaded = load_brief(p)
    assert loaded.task_id == "TSK-002"
    assert loaded.title == "Review scraper"


def test_load_brief_missing_file():
    with pytest.raises(BriefValidationError):
        load_brief("nonexistent.md")


def test_load_brief_invalid_task_type(tmp_path):
    content = """
- **agent_id**: cursor_grok
- **task_id**: TSK-003
- **task_type**: invalid_type
- **title**: Bad
"""
    p = tmp_path / "bad.md"
    p.write_text(content, encoding="utf-8")
    with pytest.raises(BriefValidationError):
        load_brief(p)


def test_package_brief():
    brief = Brief(
        agent_id="copilot",
        task_id="TSK-004",
        task_type=TaskType.REFACTORING,
        title="Refactor",
        brief_path="x",
    )
    packed = package_brief(brief)
    assert "TSK-004" in packed
    assert "copilot" in packed
