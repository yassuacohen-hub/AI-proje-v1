"""Data models for the orchestrator workflow."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    DISPATCHED = "dispatched"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REASSIGNED = "reassigned"
    REVIEWED = "reviewed"


class TaskType(str, Enum):
    CODE_REVIEW = "code_review"
    REFACTORING = "refactoring"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    DATA_TRANSFORMATION = "data_transformation"
    RESEARCH = "research"


@dataclass
class AgentManifest:
    agent_id: str
    display_name: str
    task_type: TaskType
    workspace_path: str
    max_attempts: int = 3
    timeout_seconds: int = 300
    retry_backoff_seconds: int = 2
    constraints: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["task_type"] = self.task_type.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentManifest:
        return cls(
            agent_id=data["agent_id"],
            display_name=data["display_name"],
            task_type=TaskType(data["task_type"]),
            workspace_path=data["workspace_path"],
            max_attempts=data.get("max_attempts", 3),
            timeout_seconds=data.get("timeout_seconds", 300),
            retry_backoff_seconds=data.get("retry_backoff_seconds", 2),
            constraints=data.get("constraints", {}),
        )


@dataclass
class Task:
    task_id: str
    agent_id: str
    task_type: TaskType
    brief_path: str
    context_files: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    success_criteria: list[str] = field(default_factory=list)
    deadline: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    result: TaskResult | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["task_type"] = self.task_type.value
        data["status"] = self.status.value
        if self.result is not None:
            data["result"] = self.result.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        result = None
        if data.get("result"):
            result = TaskResult.from_dict(data["result"])
        return cls(
            task_id=data["task_id"],
            agent_id=data["agent_id"],
            task_type=TaskType(data["task_type"]),
            brief_path=data["brief_path"],
            context_files=data.get("context_files", []),
            constraints=data.get("constraints", {}),
            success_criteria=data.get("success_criteria", []),
            deadline=data.get("deadline"),
            status=TaskStatus(data["status"]),
            attempts=data.get("attempts", 0),
            result=result,
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )


@dataclass
class TaskResult:
    success: bool
    output_files: list[str] = field(default_factory=list)
    summary: str = ""
    findings: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    produced_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskResult:
        return cls(
            success=data["success"],
            output_files=data.get("output_files", []),
            summary=data.get("summary", ""),
            findings=data.get("findings", []),
            metrics=data.get("metrics", {}),
            produced_at=data.get("produced_at", datetime.now().isoformat()),
        )


@dataclass
class ErrorLedgerEntry:
    task_id: str
    agent_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error_type: str = ""
    error_message: str = ""
    attempt: int = 1
    action: str = "retry"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ErrorLedgerEntry:
        return cls(
            task_id=data["task_id"],
            agent_id=data["agent_id"],
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            error_type=data.get("error_type", ""),
            error_message=data.get("error_message", ""),
            attempt=data.get("attempt", 1),
            action=data.get("action", "retry"),
        )


@dataclass
class Brief:
    agent_id: str
    task_id: str
    task_type: TaskType
    title: str
    brief_path: str
    context_files: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    success_criteria: list[str] = field(default_factory=list)
    deadline: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["task_type"] = self.task_type.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Brief:
        return cls(
            agent_id=data["agent_id"],
            task_id=data["task_id"],
            task_type=TaskType(data["task_type"]),
            title=data["title"],
            brief_path=data["brief_path"],
            context_files=data.get("context_files", []),
            constraints=data.get("constraints", {}),
            success_criteria=data.get("success_criteria", []),
            deadline=data.get("deadline"),
        )
