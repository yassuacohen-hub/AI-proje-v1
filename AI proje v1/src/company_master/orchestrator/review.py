"""Output review gate for external agent results."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from src.company_master.orchestrator.models import TaskResult
from src.company_master.orchestrator.workspace import scan_for_secrets, validate_write_path


class ReviewError(Exception):
    pass


def review_output(
    agent_id: str,
    output_path: str | Path,
    success_criteria: list[str],
) -> TaskResult:
    output_path = Path(output_path)
    if not output_path.exists():
        raise ReviewError(f"Output path does not exist: {output_path}")
    allowed = validate_write_path(agent_id, output_path)
    findings: list[str] = []
    secret_findings = scan_for_secrets(allowed)
    if secret_findings:
        findings.extend(secret_findings)
    required_files = _extract_required_files(success_criteria)
    if required_files:
        missing = _check_missing_files(allowed, required_files)
        if missing:
            findings.append(f"Missing required files: {missing}")
    file_count = _count_files(allowed)
    metrics: dict[str, Any] = {
        "file_count": file_count,
        "secret_hits": len(secret_findings),
        "missing_files": len(findings) - len(secret_findings),
    }
    success = len(findings) == 0
    summary = (
        f"Review passed: {file_count} files, no secrets, all criteria met"
        if success
        else f"Review failed: {len(findings)} findings"
    )
    return TaskResult(
        success=success,
        output_files=_collect_output_files(allowed),
        summary=summary,
        findings=findings,
        metrics=metrics,
    )


def _extract_required_files(success_criteria: list[str]) -> list[str]:
    required: list[str] = []
    for criterion in success_criteria:
        if "file:" in criterion.lower() or "dosya:" in criterion.lower():
            parts = criterion.split(":", 1)
            if len(parts) == 2:
                required.append(parts[1].strip())
    return required


def _check_missing_files(base: Path, required: list[str]) -> list[str]:
    missing = []
    for rel in required:
        if not (base / rel).exists():
            missing.append(rel)
    return missing


def _count_files(base: Path) -> int:
    if not base.exists():
        return 0
    return sum(1 for p in base.rglob("*") if p.is_file())


def _collect_output_files(base: Path) -> list[str]:
    if not base.exists():
        return []
    return [str(p.relative_to(base)) for p in sorted(base.rglob("*")) if p.is_file()]
