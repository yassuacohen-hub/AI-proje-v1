"""CLI for orchestrator workflow."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import click

from src.company_master.orchestrator.brief import BriefValidationError, load_brief
from src.company_master.orchestrator.error_ledger import ErrorLedger
from src.company_master.orchestrator.models import (
    AgentManifest,
    Task,
    TaskResult,
    TaskStatus,
)
from src.company_master.orchestrator.review import ReviewError, review_output
from src.company_master.orchestrator.runner import TaskExecutionError, run_task, execute_orchestrator_task
from src.company_master.orchestrator.sync import SyncError, append_completion, update_error_ledger_section
from src.company_master.orchestrator.task_board import gorev_ekle, gorev_guncelle, handoff_ekle
from src.company_master.orchestrator.workspace import WorkspaceViolation, resolve_workspace, validate_manifest


MANIFESTS: dict[str, AgentManifest] = {
    "cursor_grok": AgentManifest(
        agent_id="cursor_grok",
        display_name="Cursor Grok",
        task_type="code_review",
        workspace_path="workspace/external/cursor_grok",
        max_attempts=3,
        timeout_seconds=300,
    ),
    "copilot": AgentManifest(
        agent_id="copilot",
        display_name="GitHub Copilot",
        task_type="refactoring",
        workspace_path="workspace/external/copilot",
        max_attempts=3,
        timeout_seconds=300,
    ),
    "claude_code": AgentManifest(
        agent_id="claude_code",
        display_name="Claude Code",
        task_type="research",
        workspace_path="workspace/external/claude_code",
        max_attempts=3,
        timeout_seconds=300,
    ),
    "roo_code": AgentManifest(
        agent_id="roo_code",
        display_name="Roo Code",
        task_type="code_review",
        workspace_path="workspace/external/roo_code",
        max_attempts=3,
        timeout_seconds=300,
    ),
    "harici_ajan": AgentManifest(
        agent_id="harici_ajan",
        display_name="Harici Ajan (Inkling)",
        task_type="research",
        workspace_path="workspace/external/harici_ajan",
        max_attempts=3,
        timeout_seconds=300,
    ),
}

TASK_REGISTRY: dict[str, Task] = {}
ERROR_LEDGER = ErrorLedger()


@click.group()
def cli() -> None:
    """Orchestrator CLI for Huginn Data Insights external agent workflow."""
    pass


@cli.command()
@click.argument("brief_path", type=click.Path(exists=True))
@click.option("--run-mode", type=click.Choice(["orchestrator", "agent"]), default=None, help="Run mode: orchestrator or agent")
def dispatch(brief_path: str, run_mode: str | None) -> None:
    """Dispatch a brief to its external agent and run with retry/backoff.

    Orchestrator mode runs the task internally (no external agent subprocess).
    Agent mode delegates to the configured external agent with retry/backoff.
    Default mode is orchestrator when not specified.
    """
    try:
        brief = load_brief(brief_path)
    except BriefValidationError as exc:
        click.echo(f"Brief validation failed: {exc}", err=True)
        sys.exit(1)
    agent_id = brief.agent_id
    if agent_id not in MANIFESTS:
        click.echo(f"Unknown agent: {agent_id}. Available: {', '.join(MANIFESTS)}", err=True)
        sys.exit(1)
    manifest = MANIFESTS[agent_id]
    try:
        validate_manifest(manifest)
    except WorkspaceViolation as exc:
        click.echo(f"Workspace violation: {exc}", err=True)
        sys.exit(1)
    workspace = resolve_workspace(agent_id)
    click.echo(f"Dispatching {brief.task_id} to {agent_id} ({workspace})")

    # Task board'a kayıt (plan -> aktif)
    try:
        gorev_ekle(brief.task_id, brief.title, brief.agent_id,
                   oncelik="P1", dosyalar=brief.context_files or [],
                   source=brief.source, from_agent=brief.from_agent)
    except ValueError:
        # Zaten varsa mevcut kaydı aktif yap
        gorev_guncelle(brief.task_id, durum="aktif",
                       source=brief.source, from_agent=brief.from_agent)
    else:
        # Yeni eklenen görevi aktif yap
        gorev_guncelle(brief.task_id, durum="aktif",
                       source=brief.source, from_agent=brief.from_agent)

    task = Task(
        task_id=brief.task_id,
        agent_id=agent_id,
        task_type=brief.task_type,
        brief_path=str(brief_path),
        context_files=brief.context_files,
        constraints=brief.constraints,
        success_criteria=brief.success_criteria,
        deadline=brief.deadline,
        status=TaskStatus.DISPATCHED,
        source=brief.source,
    )
    TASK_REGISTRY[brief.task_id] = task
    try:
        effective_run_mode = brief.run_mode or "orchestrator"
        if effective_run_mode == "orchestrator":
            completed_task, result = execute_orchestrator_task(task, workspace)
        else:
            completed_task, result = run_task(task, manifest, ERROR_LEDGER.all())
    except TaskExecutionError as exc:
        click.echo(f"Execution error: {exc}", err=True)
        sys.exit(1)
    TASK_REGISTRY[brief.task_id] = completed_task
    click.echo(f"Task {completed_task.task_id} status: {completed_task.status.value}")
    click.echo(f"Output files: {result.output_files}")
    click.echo(f"Summary: {result.summary}")


@cli.command()
@click.argument("task_id")
@click.option("--output-dir", default=None, help="Override output directory for review")
def review(task_id: str, output_dir: str | None) -> None:
    """Review output for a completed task."""
    task = TASK_REGISTRY.get(task_id)
    if not task:
        click.echo(f"Task {task_id} not found in registry. Run dispatch first.", err=True)
        sys.exit(1)
    agent_id = task.agent_id
    manifest = MANIFESTS.get(agent_id)
    if not manifest:
        click.echo(f"Unknown agent: {agent_id}", err=True)
        sys.exit(1)
    review_path = Path(output_dir) if output_dir else Path(manifest.workspace_path) / "output"
    try:
        result = review_output(agent_id, review_path, task.success_criteria)
    except ReviewError as exc:
        click.echo(f"Review error: {exc}", err=True)
        sys.exit(1)
    status = "PASS" if result.success else "FAIL"
    click.echo(f"Review {status}: {result.summary}")
    if result.findings:
        for finding in result.findings:
            click.echo(f"  - {finding}")
    if result.success:
        task.status = TaskStatus.REVIEWED
        gorev_guncelle(task_id, durum="done", bitis=datetime.now().isoformat(timespec="seconds"))
        handoff_ekle(task_id, agent_id, str(review_path), result.summary)
        try:
            append_completion(agent_id, task_id, result.summary, result)
            click.echo(f"Appended completion to AGENT_SYNC.md")
        except SyncError as exc:
            click.echo(f"Sync warning: {exc}", err=True)
    else:
        gorev_guncelle(task_id, durum="blocked", **{"not": result.summary})


@cli.command()
def status() -> None:
    """Show active/completed tasks."""
    if not TASK_REGISTRY:
        click.echo("No tasks in registry.")
        return
    for task in TASK_REGISTRY.values():
        click.echo(
            f"{task.task_id} | {task.agent_id} | {task.status.value} | attempts={task.attempts}"
        )


@cli.command()
@click.option("--agent", default=None, help="Filter by agent_id")
@click.option("--task", default=None, help="Filter by task_id")
def errors(agent: str | None, task: str | None) -> None:
    """Show ErrorLedger entries."""
    entries = ERROR_LEDGER.all()
    if agent:
        entries = [e for e in entries if e.get("agent_id") == agent]
    if task:
        entries = [e for e in entries if e.get("task_id") == task]
    if not entries:
        click.echo("No error entries found.")
        return
    for entry in entries:
        click.echo(
            f"{entry.get('timestamp')} | {entry.get('task_id')} | {entry.get('agent_id')} | "
            f"{entry.get('error_type')} | attempt={entry.get('attempt')} | action={entry.get('action')} | {entry.get('error_message')}"
        )


@cli.command()
def sync() -> None:
    """Refresh AGENT_SYNC.md from ErrorLedger."""
    entries = ERROR_LEDGER.all()
    if not entries:
        click.echo("No error entries to sync.")
        return
    try:
        update_error_ledger_section(entries)
        click.echo(f"Synced {len(entries)} entries to AGENT_SYNC.md ErrorLedger section.")
    except SyncError as exc:
        click.echo(f"Sync failed: {exc}", err=True)
        sys.exit(1)


def main() -> int:
    cli()
    return 0


if __name__ == "__main__":
    sys.exit(main())
