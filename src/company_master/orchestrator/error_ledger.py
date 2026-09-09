"""ErrorLedger persistence for orchestrator."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.company_master.orchestrator.models import ErrorLedgerEntry


class ErrorLedger:
    def __init__(self, path: str | Path = "workspace/.error_ledger.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self._entries = data
                else:
                    self._entries = data.get("entries", [])
            except (json.JSONDecodeError, OSError):
                self._entries = []

    def _save(self) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps({"entries": self._entries}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(self.path)

    def add(self, entry: ErrorLedgerEntry) -> None:
        self._entries.append(entry.to_dict())
        self._save()

    def add_dict(self, entry: dict[str, Any]) -> None:
        self._entries.append(entry)
        self._save()

    def all(self) -> list[dict[str, Any]]:
        return list(self._entries)

    def by_task(self, task_id: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e.get("task_id") == task_id]

    def by_agent(self, agent_id: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e.get("agent_id") == agent_id]

    def clear(self) -> None:
        self._entries = []
        self._save()
