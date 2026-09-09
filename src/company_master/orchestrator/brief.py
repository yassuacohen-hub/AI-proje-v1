"""Brief packaging and validation for external agent tasks."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.company_master.orchestrator.models import Brief, TaskType, TaskStatus


class BriefValidationError(Exception):
    pass


def load_brief(path: str | Path) -> Brief:
    path = Path(path)
    if not path.exists():
        raise BriefValidationError(f"Brief file not found: {path}")
    text = path.read_text(encoding="utf-8")
    data = _parse_brief(text)
    _validate_brief(data)
    return Brief(
        agent_id=data["agent_id"],
        task_id=data["task_id"],
        task_type=TaskType(data["task_type"]),
        title=data["title"],
        brief_path=str(path),
        context_files=data.get("context_files", []),
        constraints=data.get("constraints", {}),
        success_criteria=data.get("success_criteria", []),
        deadline=data.get("deadline"),
    )


def _parse_brief(text: str) -> dict[str, Any]:
    if text.lstrip().startswith("{"):
        return json.loads(text)
    data: dict[str, Any] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("- **"):
            continue
        if ":" not in line:
            continue
        key_value = line.lstrip("- ").split(":", 1)
        if len(key_value) != 2:
            continue
        key = key_value[0].strip().lower().replace(" ", "_")
        value = key_value[1].strip()
        if key in ("context_files", "success_criteria"):
            data[key] = [v.strip() for v in value.split(",") if v.strip()]
        elif key in ("constraints",):
            data[key] = {"no_db_schema_access": True, "no_env_access": True}
        else:
            data[key] = value
    if "agent_id" not in data or "task_id" not in data or "task_type" not in data:
        raise BriefValidationError("Brief missing required fields: agent_id, task_id, task_type")
    if "title" not in data:
        data["title"] = data.get("task_id", "Untitled Task")
    return data


def _validate_brief(data: dict[str, Any]) -> None:
    required = ["agent_id", "task_id", "task_type", "title"]
    for field_name in required:
        if not data.get(field_name):
            raise BriefValidationError(f"Brief missing required field: {field_name}")
    try:
        TaskType(data["task_type"])
    except ValueError:
        raise BriefValidationError(f"Invalid task_type: {data['task_type']}")


def package_brief(brief: Brief) -> str:
    return json.dumps(brief.to_dict(), ensure_ascii=False, indent=2)
