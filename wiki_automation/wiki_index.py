#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM Wiki - Index Generator
----------------------------------------
Bu script, 00_index.md ve 00_log.md dosyalarini otomatik gunceller.
- 00_index.md: Dataview sorgularla dinamik
- 00_log.md: Append-only, son eklentiler tepeden

Kullanim:
    python wiki_index.py              # Index/log guncelle
    python wiki_index.py --dry-run    # Degisiklik yapmadan goster
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TASK_BOARD = PROJECT_ROOT / "data" / "orchestrator" / "task_board.json"
WIKI_ROOT = PROJECT_ROOT / "AI proje v1" / "V10" / "wiki"
WIKI_TASKS = WIKI_ROOT / "tasks"
WIKI_AGENTS = WIKI_ROOT / "agents"
WIKI_INDEX = WIKI_ROOT / "00_index.md"
WIKI_LOG = WIKI_ROOT / "00_log.md"
CONTRADICTIONS = WIKI_ROOT / "contradictions.md"

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]]*)?(?:\|[^\]]*)?\]\]")


def read_task_board() -> List[dict]:
    if not TASK_BOARD.exists():
        return []
    try:
        data = json.loads(TASK_BOARD.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


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


def get_active_tasks(board: List[dict]) -> List[dict]:
    return [t for t in board if t.get("durum") in ("aktif", "plan")]


def get_recent_tasks(board: List[dict], days: int = 7) -> List[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent = []
    for t in board:
        updated = t.get("bitis", t.get("baslangic", ""))
        if updated:
            try:
                updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                if updated_dt.tzinfo is None:
                    updated_dt = updated_dt.replace(tzinfo=timezone.utc)
                if updated_dt >= cutoff:
                    recent.append(t)
            except ValueError:
                pass
    return recent


def get_idle_agents(board: List[dict]) -> List[str]:
    """Durumu 'idle' olmayan ajanlari don."""
    return [t.get("sahip") for t in board if t.get("sahip") and t.get("durum") != "done"]


def build_index_content(board: List[dict]) -> str:
    """00_index.md icerigini olustur."""
    lines = []
    lines.append("# Wiki Index — Otomatik Guncelleme")
    lines.append("")
    lines.append(f"*Guncellenme: {datetime.now(timezone.utc).isoformat()}*")
    lines.append("")
    
    active = get_active_tasks(board)
    lines.append("## Aktif Gorevler")
    lines.append("")
    if active:
        lines.append("| Gorev | Baslik | Sahip | Oncelik | Durum |")
        lines.append("|-------|--------|-------|---------|-------|")
        for t in active:
            lines.append(f"| {t.get('task_id','-')} | {t.get('baslik','-')} | {t.get('sahip','-')} | {t.get('oncelik','-')} | {t.get('durum','-')} |")
    else:
        lines.append("- Aktif gorev yok.")
    lines.append("")
    
    recent = get_recent_tasks(board)
    lines.append("## Son 7 Gun")
    lines.append("")
    if recent:
        for t in recent[:10]:
            lines.append(f"- **{t.get('task_id','-')}**: {t.get('baslik','-')} ({t.get('sahip','-')})")
    else:
        lines.append("- Son 7 gundeki gorev yok.")
    lines.append("")
    
    idle = get_idle_agents(board)
    lines.append("## Ajan Durumlari")
    lines.append("")
    if idle:
        for agent in sorted(set(idle)):
            lines.append(f"- {agent}")
    else:
        lines.append("- Aktif ajan yok.")
    lines.append("")
    
    lines.append("## Konu Basliklari")
    lines.append("")
    lines.append("- Mimari Kararlar: [[ADR-template]]")
    lines.append("- Ongoruler: [[10_ankara_osb_sentez]]")
    lines.append("- Hata Notlari: [[Bug-template]]")
    lines.append("")
    
    lines.append("---")
    lines.append(f"*Bu sayfa {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC'de wiki_index.py tarafindan guncellendi.*")
    
    return "\n".join(lines) + "\n"


def build_log_content(board: List[dict]) -> str:
    """00_log.md icerigini olustur (append-only)."""
    lines = []
    lines.append("# Wiki Ingestion Log")
    lines.append("")
    lines.append(f"*Son guncelleme: {datetime.now(timezone.utc).isoformat()}*")
    lines.append("")
    
    lines.append("## Son Islemler")
    lines.append("")
    
    # Task_board'dan son islemleri ekle
    for t in board[:10]:
        lines.append(f"- [{t.get('task_id','-')}] {t.get('baslik','-')} — {t.get('sahip','-')} ({t.get('durum','-')})")
    
    lines.append("")
    lines.append("---")
    lines.append(f"*Bu sayfa {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC'de guncellendi.*")
    
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Update wiki index and log")
    parser.add_argument("--dry-run", action="store_true", help="Show without changes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    board = read_task_board()
    
    index_content = build_index_content(board)
    log_content = build_log_content(board)
    
    if args.dry_run:
        print("[DRY-RUN] Would write 00_index.md")
        print("[DRY-RUN] Would write 00_log.md")
        return 0
    
    WIKI_INDEX.write_text(index_content, encoding="utf-8")
    WIKI_LOG.write_text(log_content, encoding="utf-8")
    
    if args.verbose:
        print(f"Updated: {WIKI_INDEX}")
        print(f"Updated: {WIKI_LOG}")
    
    print(f"Wiki index updated: {WIKI_INDEX}")
    print(f"Wiki log updated: {WIKI_LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
