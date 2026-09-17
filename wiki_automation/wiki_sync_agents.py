#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM Wiki - Agent Sync Script
----------------------------------------
Bu script, task_board.json'daki ajan bilgilerini okuyup
AI proje v1/V10/wiki/agents/{agent_id}.md dosyalarina yazar.
Her ajanin aktif gorevleri, son aktiviteleri ve ortalama sureleri gosterilir.

Kullanim:
    python wiki_sync_agents.py              # Tum ajanlari sync et
    python wiki_sync_agents.py --agent copilot  # Sadece copilot
    python wiki_sync_agents.py --dry-run    # Degisiklik yapmadan goster
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TASK_BOARD = PROJECT_ROOT / "data" / "orchestrator" / "task_board.json"
WIKI_ROOT = PROJECT_ROOT / "AI proje v1" / "V10" / "wiki"
WIKI_AGENTS = WIKI_ROOT / "agents"
WIKI_LOG = WIKI_ROOT / "00_log.md"

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]]*)?(?:\|[^\]]*)?\]\]")

AGENT_TYPE_MAP = {
    "claude_code": {"role": "harici", "tool": "Kimi Code"},
    "copilot": {"role": "harici", "tool": "GitHub Copilot"},
    "cursor_grok": {"role": "harici", "tool": "Cursor Grok"},
    "harici_ajan": {"role": "harici", "tool": "Custom"},
}

INTERNAL_AGENTS = {
    "koordinator", "mimar", "arastirmaci", "gelistirici",
    "kalite", "web_kazima"
}

ALL_AGENTS = set(AGENT_TYPE_MAP.keys()) | INTERNAL_AGENTS


def frontmatter_extract(text: str) -> Tuple[Dict[str, str], str]:
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) >= 3:
            meta = {}
            for line in parts[1].splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    meta[key.strip().lower()] = val.strip().strip('"\\\'')
            return meta, parts[2]
    return {}, text


def frontmatter_create(meta: Dict[str, str]) -> str:
    if not meta:
        return ""
    lines = ["---"]
    for key, value in meta.items():
        lines.append(f"{key}: {value}")
    lines.append("---\n")
    return "\n".join(lines)


def read_task_board() -> List[dict]:
    if not TASK_BOARD.exists():
        return []
    try:
        data = json.loads(TASK_BOARD.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def get_agent_tasks(board: List[dict], agent_id: str) -> List[dict]:
    """Agent'in aktif gorevlerini don."""
    return [t for t in board if t.get("sahip") == agent_id and t.get("durum") != "done"]


def get_completed_tasks(board: List[dict], agent_id: str, days: int = 7) -> List[dict]:
    """Son N gunde tamamlanan gorevleri don."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    completed = []
    for t in board:
        if t.get("sahip") == agent_id and t.get("durum") == "done":
            bitis = t.get("bitis", "")
            if bitis:
                try:
                    bitis_dt = datetime.fromisoformat(bitis.replace("Z", "+00:00"))
                    # Offset-naive datetimes'i offset-aware yap
                    if bitis_dt.tzinfo is None:
                        bitis_dt = bitis_dt.replace(tzinfo=timezone.utc)
                    if bitis_dt >= cutoff:
                        completed.append(t)
                except ValueError:
                    pass
    return completed


def build_agent_page(agent_id: str, board: List[dict]) -> str:
    """Agent icin wiki sayfa icerigi olustur."""
    active_tasks = get_agent_tasks(board, agent_id)
    completed = get_completed_tasks(board, agent_id)

    lines = []
    lines.append(f"# {agent_id}")
    lines.append("")

    agent_info = AGENT_TYPE_MAP.get(agent_id, {"role": "internal", "tool": "Custom"})
    lines.append(f"- **Tip:** {agent_info['role']}")
    lines.append(f"- **Araclar:** {agent_info['tool']}")
    lines.append(f"- **Guncellenme:** {datetime.now(timezone.utc).isoformat()}")
    lines.append("")

    lines.append("## Aktif Gorevler")
    lines.append("")
    if active_tasks:
        lines.append("| Gorev | Baslik | Oncelik | Durum |")
        lines.append("|-------|--------|---------|-------|")
        for t in active_tasks:
            lines.append(f"| {t.get('task_id','-')} | {t.get('baslik','-')} | {t.get('oncelik','-')} | {t.get('durum','-')} |")
    else:
        lines.append("- Aktif gorev yok.")
    lines.append("")

    lines.append("## Son Tamamlanan Gorevler")
    lines.append("")
    if completed:
        for t in completed[:5]:
            lines.append(f"- **{t.get('task_id','-')}**: {t.get('baslik','-')} ({t.get('bitis','-')})")
    else:
        lines.append("- Son tamamlanan gorev yok.")
    lines.append("")

    if active_tasks or completed:
        lines.append("---")
        lines.append(f"*Bu sayfa {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC'de wiki_sync_agents.py tarafindan olusturuldu.*")

    return "\n".join(lines) + "\n"


def update_wiki_log(agent_id: str, count: int) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    log_entry = f"## [{timestamp}] wiki_sync_agents - {agent_id}\n- Agent pages updated: {count}\n\n---\n\n"
    if WIKI_LOG.exists():
        current_log = WIKI_LOG.read_text(encoding="utf-8")
        new_log = log_entry + current_log
    else:
        new_log = "# Wiki Ingestion Log\n\n---\n\n" + log_entry
    WIKI_LOG.write_text(new_log, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync agent info to LLM wiki")
    parser.add_argument("--agent", help="Specific agent to sync")
    parser.add_argument("--dry-run", action="store_true", help="Show without changes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    WIKI_AGENTS.mkdir(parents=True, exist_ok=True)

    board = read_task_board()
    if args.agent:
        agents = [args.agent] if args.agent in ALL_AGENTS else []
        if not agents:
            print(f"Error: Unknown agent '{args.agent}'. Available: {', '.join(sorted(ALL_AGENTS))}")
            return 1
    else:
        agents = sorted(ALL_AGENTS)

    total = 0
    for agent_id in agents:
        content = build_agent_page(agent_id, board)
        agent_file = WIKI_AGENTS / f"{agent_id}.md"

        if args.dry_run:
            print(f"[DRY-RUN] Would write: {agent_file}")
            total += 1
        else:
            agent_file.write_text(content, encoding="utf-8")
            total += 1
            if args.verbose:
                print(f"Updated: {agent_file}")

        if not args.dry_run:
            update_wiki_log(agent_id, total)

    print(f"\n=== Wiki Agent Sync Summary ===")
    print(f"Agents synced: {total}")
    if not args.dry_run:
        print(f"Log updated: {WIKI_LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
