#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Task Wrapper - Task board harici ad-hoc gorevler icin.

Kullanim:
    python scripts/quick_task.py --from-agent roo_code --agent claude_code --task CLAUDE-01 --title "Arastirma" --task-type research --run-mode orchestrator --review

Bu script:
1. workspace/external/<agent>/brief_<task_id>.md olusturur
2. orchestrator dispatch calistirir (task board'a kayit olur)
3. --review verilirse review de calistirir (handoff + AGENT_SYNC guncellenir)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.company_master.orchestrator.cli import cli as orchestrator_cli
from src.company_master.orchestrator.brief import Brief, BriefValidationError, TaskType

WORKSPACE_ROOT = ROOT / "workspace" / "external"


def brief_olustur(agent_id: str, task_id: str, title: str,
                  task_type: TaskType | str = TaskType.RESEARCH,
                  from_agent: str | None = None,
                  source: str = "harici",
                  run_mode: str | None = None,
                  context_files: list[str] | None = None,
                  success_criteria: list[str] | None = None) -> Path:
    agent_ws = WORKSPACE_ROOT / agent_id
    agent_ws.mkdir(parents=True, exist_ok=True)
    brief_path = agent_ws / f"brief_{task_id}.md"
    if isinstance(task_type, str):
        task_type = TaskType(task_type)
    brief = Brief(
        agent_id=agent_id,
        task_id=task_id,
        task_type=task_type,
        title=title,
        brief_path=str(brief_path),
        context_files=context_files or [],
        constraints={},
        success_criteria=success_criteria or [],
        deadline=None,
        source=source,
        from_agent=from_agent,
        run_mode=run_mode,
    )
    brief_path.write_text(brief.package(), encoding="utf-8")
    return brief_path


def main() -> int:
    p = argparse.ArgumentParser(description="Quick task wrapper for orchestrator")
    p.add_argument("--from-agent", required=True, help="Gorevi atayan ajan (orn. roo_code)")
    p.add_argument("--agent", required=True, help="Gorevi calistiracan ajan (orn. claude_code)")
    p.add_argument("--task", required=True, dest="task_id", help="Gorev tanimlayici")
    p.add_argument("--title", required=True, help="Gorev basligi")
    p.add_argument("--task-type", choices=[t.value for t in TaskType], default=TaskType.RESEARCH.value, help="Gorev tipi (default: research)")
    p.add_argument("--context", nargs="*", default=[], help="Baglam dosyalari")
    p.add_argument("--criteria", nargs="*", default=[], help="Basari kriterleri")
    p.add_argument("--run-mode", choices=["orchestrator", "agent"], default="orchestrator", help="Calistirma modu: orchestrator ya da ajan (default: orchestrator)")
    p.add_argument("--review", action="store_true", help="Dispatch sonrasi review calistir")
    p.add_argument("--push-dosyalar", nargs="*", default=None, metavar="DOSYA",
                   help="Review basariliysa bu dosyalari secmeli commit+push et (hibrit push; koordinasyon dosyalari otomatik dahil)")
    args = p.parse_args()

    try:
        brief_path = brief_olustur(
            agent_id=args.agent,
            task_id=args.task_id,
            title=args.title,
            task_type=args.task_type,
            from_agent=args.from_agent,
            source="harici",
            run_mode=args.run_mode,
            context_files=args.context,
            success_criteria=args.criteria,
        )
    except BriefValidationError as exc:
        print(f"Brief hatasi: {exc}", file=sys.stderr)
        return 1

    sys.argv = ["orchestrator", "dispatch", "--run-mode", args.run_mode, str(brief_path)]
    try:
        orchestrator_cli()
    except SystemExit as exc:
        if exc.code != 0:
            print(f"Dispatch basarisiz (kod {exc.code})", file=sys.stderr)
            return exc.code or 1

    if args.review:
        sys.argv = ["orchestrator", "review", args.task_id]
        try:
            orchestrator_cli()
        except SystemExit as exc:
            # ORCH-01 duzeltmesi: click basarida SystemExit(0) firlatir;
            # "exc.code or 1" bu 0'i 1'e cevirip basarili akisi basarisiz
            # gösteriyordu. 0 -> 0, None -> 0, 1 -> 1 olacak sekilde duzeltildi.
            kod = exc.code or 0
            if kod != 0:
                return kod
        # GIT-01 hibrit push: review basariliysa ve --push-dosyalar verildiyse
        # yalniz bu gorevin dosyalari + koordinasyon dosyalari secmeli push edilir.
        if args.push_dosyalar is not None:
            r = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "git_push_gorev.py"),
                 "--mesaj", f"{args.task_id}: ajan gorevi tamamlandi (quick_task)",
                 *args.push_dosyalar],
                cwd=str(ROOT), check=False,
            )
            if r.returncode != 0:
                print(f"Uyari: otomatik push basarisiz (kod {r.returncode})", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
