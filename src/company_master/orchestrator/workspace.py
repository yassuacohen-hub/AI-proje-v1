"""Workspace isolation enforcement for external agents."""
from __future__ import annotations

import os
from pathlib import Path

from src.company_master.orchestrator.models import AgentManifest


ALLOWED_WORKSPACE_ROOT = Path("workspace/external")
SECRET_PATTERNS = [
    r"(?i)(api_key|secret|token|password|passwd|pwd)\s*[:=]\s*[\"'][^\"']+[\"']",
    r"(?i)(aws_access_key_id|aws_secret_access_key)\s*[:=]\s*[\"'][^\"']+[\"']",
    r"(?i)(sk-|ghp-|github_pat_|xox[baprs]-)[a-zA-Z0-9]{10,}",
    r"(?i)(postgresql|mysql|mongodb)://[^:]+:[^@]+@",
    r"(?i)bearer\s+[a-zA-Z0-9\-._~+/]+=*",
]


class WorkspaceViolation(Exception):
    """Raised when an agent attempts to write outside its allowed workspace."""


def resolve_workspace(agent_id: str) -> Path:
    workspace = ALLOWED_WORKSPACE_ROOT / agent_id
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace.resolve()


def validate_write_path(agent_id: str, target_path: str | Path) -> Path:
    allowed = resolve_workspace(agent_id)
    target = Path(target_path).resolve()
    if not str(target).startswith(str(allowed)):
        raise WorkspaceViolation(
            f"Agent {agent_id} attempted to write outside workspace: {target} -> allowed: {allowed}"
        )
    return target


def validate_manifest(manifest: AgentManifest) -> None:
    if not manifest.agent_id:
        raise ValueError("agent_id is required")
    if not manifest.workspace_path:
        raise ValueError("workspace_path is required")
    workspace = Path(manifest.workspace_path).resolve()
    if not str(workspace).startswith(str(ALLOWED_WORKSPACE_ROOT.resolve())):
        raise WorkspaceViolation(
            f"Manifest workspace outside allowed root: {workspace}"
        )


def scan_for_secrets(path: str | Path) -> list[str]:
    findings: list[str] = []
    target = Path(path)
    if target.is_file():
        _scan_file(target, findings)
    elif target.is_dir():
        for file_path in target.rglob("*"):
            if file_path.is_file():
                _scan_file(file_path, findings)
    return findings


def _scan_file(file_path: Path, findings: list[str]) -> None:
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return
    import re
    for pattern in SECRET_PATTERNS:
        for match in re.finditer(pattern, text):
            line_no = text[: match.start()].count("\n") + 1
            findings.append(
                f"{file_path}:{line_no}: possible secret ({pattern[:40]}...)"
            )


def enforce_isolation(agent_id: str, output_path: str | Path) -> Path:
    validate_write_path(agent_id, output_path)
    return Path(output_path).resolve()
