#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wiki Automation Orkestrator
==========================
Calistir:
    python wiki_automation/run_all.py [--fix] [--ci] [--commit]

Sira:
    1. wiki_ingest.py       — yeni/duzenlenmis sayfalari tespit et
    2. wiki_sync_agents.py  — task_board agent dosyalarini senkronize et
    3. wiki_lint.py         — saglik kontrolu (--fix, --ci)
    4. wiki_index.py        — index.json güncelle
    5. git add + commit     (--commit ile)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WIKI_AUTO = PROJECT_ROOT / "wiki_automation"

SCRIPTS = [
    "wiki_ingest.py",
    "wiki_sync_agents.py",
    "wiki_lint.py",
    "wiki_index.py",
]


def run_script(script: str, args: list[str]) -> int:
    cmd = [sys.executable, str(WIKI_AUTO / script)] + args
    print(f"\n>>> Calistiriliyor: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return result.returncode


def git_commit() -> int:
    week = datetime.now(timezone.utc).isocalendar()[1]
    msg = f"Y{week}: auto-wiki update"
    print(f"\n>>> git commit: {msg}")
    subprocess.run(["git", "add", "-A"], cwd=str(PROJECT_ROOT), check=False)
    r = subprocess.run(["git", "commit", "-m", msg], cwd=str(PROJECT_ROOT))
    return r.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Wiki automation orkestratoru")
    parser.add_argument("--fix", action="store_true", help="wiki_lint --fix calistir")
    parser.add_argument("--ci", action="store_true", help="wiki_lint --ci calistir")
    parser.add_argument("--commit", action="store_true", help="Git commit yap")
    parser.add_argument("--skip-ingest", action="store_true", help="wiki_ingest.py atla")
    parser.add_argument("--skip-sync", action="store_true", help="wiki_sync_agents.py atla")
    parser.add_argument("--skip-index", action="store_true", help="wiki_index.py atla")
    args = parser.parse_args()

    lint_args = []
    if args.fix:
        lint_args.append("--fix")
    if args.ci:
        lint_args.append("--ci")

    failed = []

    if not args.skip_ingest:
        rc = run_script("wiki_ingest.py", [])
        if rc != 0:
            failed.append("wiki_ingest.py")

    if not args.skip_sync:
        rc = run_script("wiki_sync_agents.py", [])
        if rc != 0:
            failed.append("wiki_sync_agents.py")

    if lint_args:
        rc = run_script("wiki_lint.py", lint_args)
        if rc != 0:
            failed.append("wiki_lint.py")

    if not args.skip_index:
        rc = run_script("wiki_index.py", [])
        if rc != 0:
            failed.append("wiki_index.py")

    if args.commit and not failed:
        rc = git_commit()
        if rc != 0:
            failed.append("git commit")

    if failed:
        print(f"\n!!! Hata: {', '.join(failed)}")
        return 1

    print("\n=== Tum adimlar basariyla tamamlandi ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
