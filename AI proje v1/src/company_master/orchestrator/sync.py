"""AGENT_SYNC.md updater for orchestrator."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from src.company_master.orchestrator.models import TaskResult


AGENT_SYNC_PATH = Path("AGENT_SYNC.md")


class SyncError(Exception):
    pass


def append_completion(
    agent_name: str,
    task_id: str,
    description: str,
    result: TaskResult | None = None,
) -> None:
    if not AGENT_SYNC_PATH.exists():
        raise SyncError(f"AGENT_SYNC.md not found at {AGENT_SYNC_PATH}")
    content = AGENT_SYNC_PATH.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")
    summary = result.summary if result and result.summary else description
    entry = f"| {agent_name} | {today} | {task_id}: {summary} |"
    marker = "## Tamamlananlar (Senkron Kaydi)"
    if marker not in content:
        raise SyncError("AGENT_SYNC.md missing 'Tamamlananlar' section")
    new_content = content.replace(marker, f"{marker}\n\n| {agent_name} | {today} | {task_id}: {summary} |")
    AGENT_SYNC_PATH.write_text(new_content, encoding="utf-8")


def update_error_ledger_section(entries: list[dict[str, Any]]) -> None:
    if not AGENT_SYNC_PATH.exists():
        raise SyncError(f"AGENT_SYNC.md not found at {AGENT_SYNC_PATH}")
    content = AGENT_SYNC_PATH.read_text(encoding="utf-8")
    table_lines = ["| task_id | agent_id | timestamp | error_type | error_message | attempt | aksiyon |",
                   "|---------|----------|-----------|------------|---------------|---------|---------|"]
    for entry in entries:
        msg = _truncate(entry.get("error_message", ""), 80)
        table_lines.append(
            f"| {entry.get('task_id', '')} | {entry.get('agent_id', '')} | {entry.get('timestamp', '')} | {entry.get('error_type', '')} | {msg} | {entry.get('attempt', '')} | {entry.get('action', '')} |"
        )
    table = "\n".join(table_lines)
    marker = "## ErrorLedger"
    if marker in content:
        new_content = re.sub(
            r"## ErrorLedger.*",
            f"{marker}\n\n{table}\n",
            content,
            flags=re.DOTALL,
        )
    else:
        new_content = content.rstrip() + f"\n\n## ErrorLedger\n\n{table}\n"
    AGENT_SYNC_PATH.write_text(new_content, encoding="utf-8")


def _truncate(text: str, length: int) -> str:
    text = text.replace("|", "/").replace("\n", " ")
    return text[:length] + "..." if len(text) > length else text
