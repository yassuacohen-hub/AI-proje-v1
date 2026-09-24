"""Task execution runner with retry/backoff and timeout."""
from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

from src.company_master.orchestrator.models import (
    AgentManifest,
    ErrorLedgerEntry,
    Task,
    TaskResult,
    TaskStatus,
)


class TaskExecutionError(Exception):
    def __init__(self, message: str, error_type: str = "execution_error"):
        super().__init__(message)
        self.error_type = error_type


def run_task(
    task: Task,
    manifest: AgentManifest,
    ledger: list[ErrorLedgerEntry],
) -> tuple[Task, TaskResult]:
    last_error = None
    for attempt in range(1, manifest.max_attempts + 1):
        task.attempts = attempt
        task.status = TaskStatus.RUNNING
        task.updated_at = _now()
        try:
            result = _execute(task, manifest)
            task.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
            task.result = result
            task.updated_at = _now()
            return task, result
        except TaskExecutionError as exc:
            last_error = exc
            entry = ErrorLedgerEntry(
                task_id=task.task_id,
                agent_id=task.agent_id,
                error_type=exc.error_type,
                error_message=str(exc),
                attempt=attempt,
                action="retry" if attempt < manifest.max_attempts else "reassign",
            )
            ledger.append(entry)
            if attempt < manifest.max_attempts:
                backoff = manifest.retry_backoff_seconds * (2 ** (attempt - 1))
                time.sleep(backoff)
    task.status = TaskStatus.REASSIGNED
    task.updated_at = _now()
    result = TaskResult(
        success=False,
        summary=f"Task failed after {manifest.max_attempts} attempts: {last_error}",
        findings=[str(last_error)] if last_error else [],
    )
    task.result = result
    return task, result


def _execute(task: Task, manifest: AgentManifest) -> TaskResult:
    workspace = Path(manifest.workspace_path)
    output_dir = workspace / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "python",
        str(workspace / "run.py"),
        "--task-id", task.task_id,
        "--brief", task.brief_path,
        "--output-dir", str(output_dir),
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=manifest.timeout_seconds,
            cwd=str(workspace),
        )
    except subprocess.TimeoutExpired as exc:
        raise TaskExecutionError(
            f"Task timed out after {manifest.timeout_seconds}s",
            error_type="timeout",
        ) from exc
    except FileNotFoundError as exc:
        raise TaskExecutionError(
            f"Agent runner not found: {workspace / 'run.py'}",
            error_type="runner_not_found",
        ) from exc
    except Exception as exc:
        raise TaskExecutionError(f"Unexpected execution error: {exc}") from exc
    if proc.returncode != 0:
        stderr = proc.stderr.strip()[-500:] if proc.stderr else ""
        raise TaskExecutionError(
            f"Agent process failed (rc={proc.returncode}): {stderr}",
            error_type="process_failure",
        )
    output_files = _collect_output_files(output_dir)
    summary = proc.stdout.strip()[-1000:] if proc.stdout else ""
    return TaskResult(
        success=True,
        output_files=output_files,
        summary=summary,
        metrics={"returncode": proc.returncode, "stdout_len": len(proc.stdout or "")},
    )


def _collect_output_files(output_dir: Path) -> list[str]:
    if not output_dir.exists():
        return []
    return [
        str(p.relative_to(output_dir))
        for p in sorted(output_dir.rglob("*"))
        if p.is_file()
    ]


def _now() -> str:
    from datetime import datetime
    return datetime.now().isoformat()
