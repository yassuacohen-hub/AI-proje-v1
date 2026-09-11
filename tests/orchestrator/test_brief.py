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


def test_package_brief_and_brief_package_equivalence():
    """Test that package_brief() and Brief.package() produce identical output.
    
    This addresses the issue where brief.py had its own package_brief() function
    while Brief already had a package() method. Both should produce the same
    JSON output for the same Brief object.
    """
    brief = Brief(
        agent_id="test_agent",
        task_id="TEST-BRIEF-001",
        task_type=TaskType.RESEARCH,
        title="Test Brief",
        brief_path="workspace/external/test_agent/brief.md",
        context_files=["docs/test.md"],
        constraints={"no_db_schema_access": True, "no_env_access": True},
        success_criteria=["Test criterion 1", "Test criterion 2"],
        deadline="2026-09-12",
        source="harici",
        from_agent="test_agent",
        run_mode="orchestrator",
    )

    package_brief_output = package_brief(brief)
    brief_package_output = brief.package()

    # Both should be valid JSON
    assert json.loads(package_brief_output)
    assert json.loads(brief_package_output)

    # Both should be equivalent
    assert json.loads(package_brief_output) == json.loads(brief_package_output)

    # Both should include all fields
    data = json.loads(package_brief_output)
    assert data["agent_id"] == "test_agent"
    assert data["task_id"] == "TEST-BRIEF-001"
    assert data["task_type"] == "research"
    assert data["title"] == "Test Brief"
    assert data["context_files"] == ["docs/test.md"]
    assert data["constraints"]["no_db_schema_access"] is True
    assert data["constraints"]["no_env_access"] is True
    assert data["success_criteria"] == ["Test criterion 1", "Test criterion 2"]
    assert data["deadline"] == "2026-09-12"
    assert data["source"] == "harici"
    assert data["from_agent"] == "test_agent"
    assert data["run_mode"] == "orchestrator"


def test_load_brief_and_package_roundtrip():
    """Test that load_brief() + package_brief() round-trips correctly."""
    # Create a temporary brief file
    brief_path = Path("workspace/external/test_agent/roundtrip_brief.md")
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    brief_path.write_text(
        json.dumps({
            "agent_id": "test_agent",
            "task_id": "TEST-ROUNDTRIP",
            "task_type": "research",
            "title": "Roundtrip Brief",
            "brief_path": str(brief_path),
            "context_files": ["docs/roundtrip.md"],
            "constraints": {"no_db_schema_access": True, "no_env_access": True},
            "success_criteria": ["Roundtrip criterion"],
            "deadline": "2026-09-13",
            "source": "harici",
            "from_agent": "test_agent",
            "run_mode": "orchestrator",
        }),
        encoding="utf-8",
    )

    loaded_brief = load_brief(brief_path)
    packed = package_brief(loaded_brief)

    assert json.loads(packed)["task_id"] == "TEST-ROUNDTRIP"
    assert json.loads(packed)["title"] == "Roundtrip Brief"
    assert json.loads(packed)["context_files"] == ["docs/roundtrip.md"]
    assert json.loads(packed)["constraints"]["no_db_schema_access"] is True
    assert json.loads(packed)["constraints"]["no_env_access"] is True
    assert json.loads(packed)["success_criteria"] == ["Roundtrip criterion"]
    assert json.loads(packed)["deadline"] == "2026-09-13"
    assert json.loads(packed)["source"] == "harici"
    assert json.loads(packed)["from_agent"] == "test_agent"
    assert json.loads(packed)["run_mode"] == "orchestrator"
