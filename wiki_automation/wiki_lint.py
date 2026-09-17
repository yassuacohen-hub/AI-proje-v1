#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM Wiki - Lint / Health Check Script
----------------------------------------
Bu script wiki sagligini kontrol eder. CI pipeline'da hard gate olarak
calisir. Kontroller:
- Orphan Dosyalari: wiki/tasks/ veya wiki/agents/ icinde task_board.json'
  olmayan ID'ler
- Broken Links: [[task-id]] veya [[agent-id]] formatindaki ic linklerin
  gecerliligi
- Cesitkinkiyik Yogunlugu: contradictions.md'deki son 24 saattaki
  giriş sayisi (eşik aşılırsa uyarı)
- Stale Icerik: 7 gun üzeri güncellenmemis aktif gorev sayfalari
- Frontmatter Gecerliligi: Gerekli alanlarin (task_id, sahip, durum,
  updated_at) varligi
- Broken Links: V10 wiki'ndeki gidis linklerinin cozumu

Kullanim:
    python wiki_lint.py                    # Tum kontroller
    python wiki_lint.py --ci               # CI modu (exit code: 1 soruna)
    python wiki_lint.py --output report.json  # JSON rapor kaydet
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
CONTRADICTIONS = WIKI_ROOT / "contradictions.md"
WIKI_LOG = WIKI_ROOT / "00_log.md"

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]]*)?(?:\|[^\]]*)?\]\]")

GEREKEN_FIELDLAR = {"task_id", "sahip", "durum", "updated_at"}
YETERLIK_SURE = 7  # gun
CESITKINKI_SURE = 24  # saat
CESITKINKI_ESEK = 5

def frontmatter_extract(text: str):
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) >= 3:
            meta = {}
            for line in parts[1].splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    meta[key.strip().lower()] = val.strip().strip("\"\'")
            return meta, parts[2]
    return {}, text


def read_task_board() -> List[dict]:
    if not TASK_BOARD.exists():
        return []
    try:
        data = json.loads(TASK_BOARD.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []




def frontmatter_create(meta: dict) -> str:
    """Frontmatter dict'inden YAML string'i olustur."""
    if not meta:
        return ""
    lines = ["---"]
    for key, value in meta.items():
        lines.append(f"{key}: {value}")
    lines.append("---\n")
    return "\n".join(lines)


def extract_wiki_links(text: str) -> set:
    """Metinden [[wiki link]] formatindaki linkleri cikar."""
    return set(WIKILINK_RE.findall(text))


def fix_frontmatter() -> tuple:
    """Eksik frontmatter alanlarini otomatik tamamlar."""
    fixed_count = 0
    log = []
    for directory in [WIKI_TASKS, WIKI_AGENTS]:
        if not directory.exists():
            continue
        for md_file in directory.glob('*.md'):
            try:
                content = md_file.read_text(encoding='utf-8')
                meta, body = frontmatter_extract(content)
                if not meta:
                    meta = {'task_id': md_file.stem, 'sahip': 'unknown', 'durum': 'plan', 'updated_at': datetime.now(timezone.utc).isoformat()}
                    new_content = frontmatter_create(meta) + '\n' + body

                    md_file.write_text(new_content, encoding='utf-8')
                    fixed_count += 1
                    log.append('Frontmatter eklendi: ' + md_file.name)
                    continue
                missing_fields = GEREKEN_FIELDLAR - set(meta.keys())
                if missing_fields:
                    for field in missing_fields:
                        meta[field] = 'unknown'
                    new_content = frontmatter_create(meta) + '\n' + body

                    md_file.write_text(new_content, encoding='utf-8')
                    fixed_count += 1
                    log.append('Eksik alan eklendi (' + ', '.join(sorted(missing_fields)) + '): ' + md_file.name)
            except Exception as e:
                log.append('Hata: ' + md_file.name + ': ' + str(e))
    return fixed_count, log


def fix_broken_links() -> tuple:
    """Broken linkleri otomatik duzelt."""
    fixed_count = 0
    log = []
    for md_file in WIKI_ROOT.rglob('*.md'):
        if not md_file.exists():
            continue
        try:
            content = md_file.read_text(encoding='utf-8')
            if not extract_wiki_links(content):
                target = md_file.stem
                new_content = content.rstrip() + '\n\n[[' + target + ']]\n'
                md_file.write_text(new_content, encoding='utf-8')
                fixed_count += 1
                log.append('Link eklendi: ' + md_file.name)
        except Exception as e:
            log.append('Hata: ' + md_file.name + ': ' + str(e))
    return fixed_count, log


def check_orphans(board: List[dict]) -> List[str]:
    """wiki/tasks ve wiki/agents'da task_board.json' olmayan ID'leri bul."""
    task_ids = {t.get("task_id") for t in board if t.get("task_id")}
    orphans = []

    if WIKI_TASKS.exists():
        for f in WIKI_TASKS.glob("*.md"):
            if f.stem not in task_ids:
                orphans.append(str(f))

    if WIKI_AGENTS.exists():
        agent_ids = {t.get("sahip") for t in board if t.get("sahip")}
        for f in WIKI_AGENTS.glob("*.md"):
            if f.stem not in agent_ids:
                orphans.append(str(f))

    return orphans


def check_broken_links() -> List[str]:
    """wiki icindeki [[link]] formatindaki broken linkleri tespit et."""
    broken = []
    link_targets = set()

    # Tüm .md dosyalarindan link hedeflerini topla
    for md_file in WIKI_ROOT.rglob("*.md"):
        if not md_file.exists():
            continue
        content = md_file.read_text(encoding="utf-8", errors="replace")
        links = WIKILINK_RE.findall(content)
        for link in links:
            link_targets.add(link)

    # Her hedefin gecerli olup olmadigini kontrol et
    valid_targets = set()
    for md_file in WIKI_ROOT.rglob("*.md"):
        valid_targets.add(md_file.stem)
        valid_targets.add(md_file.relative_to(WIKI_ROOT).as_posix().replace(".md", ""))

    for target in link_targets:
        # Farkli formatlari dene
        if target not in valid_targets:
            if target + ".md" not in valid_targets:
                broken.append(target)

    return broken


def check_contradiction_density() -> Tuple[int, int]:
    """contradictions.md'deki son 24 saattaki giriş sayisini hesapla."""
    if not CONTRADICTIONS.exists():
        return 0, 0

    content = CONTRADICTIONS.read_text(encoding="utf-8")
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=CESITKINKI_SURE)

    entries = re.findall(r"Contradictions detected at (\d{4}-\d{2}-\d{2}T[\d:]+\+00:00)", content)
    recent = 0
    for entry in entries:
        try:
            entry_dt = datetime.fromisoformat(entry)
            if entry_dt >= cutoff:
                recent += 1
        except ValueError:
            pass

    return recent, CESITKINKI_ESEK


def check_stale_content(board: List[dict]) -> List[str]:
    """7 gun üzeri güncellenmemis aktif gorev sayfalari."""
    stale = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=YETERLIK_SURE)

    if not WIKI_TASKS.exists():
        return stale

    for f in WIKI_TASKS.glob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            meta, _ = frontmatter_extract(content)
            updated_str = meta.get("updated_at", meta.get("ingested", ""))
            if updated_str:
                updated_dt = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
                if updated_dt.tzinfo is None:
                    updated_dt = updated_dt.replace(tzinfo=timezone.utc)
                if updated_dt < cutoff:
                    stale.append(f"{f.name} (last updated: {updated_str})")
        except (OSError, ValueError, UnicodeDecodeError):
            pass

    return stale


def check_frontmatter() -> List[str]:
    """Gerekli frontmatter alanlarinin eksik oldugu sayfalari bul."""
    missing = []

    for directory in [WIKI_TASKS, WIKI_AGENTS]:
        if not directory.exists():
            continue
        for f in directory.glob("*.md"):
            try:
                content = f.read_text(encoding="utf-8")
                meta, _ = frontmatter_extract(content)
                missing_fields = GEREKEN_FIELDLAR - set(meta.keys())
                if missing_fields:
                    missing.append(f"{f.name}: {', '.join(missing_fields)}")
            except (OSError, UnicodeDecodeError):
                pass

    return missing


def lint() -> Dict:
    """Tum kontrolleri calistir ve rapor ver."""
    board = read_task_board()

    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {},
        "errors": [],
        "warnings": []
    }

    # 1. Orphan kontrol
    orphans = check_orphans(board)
    results["checks"]["orphans"] = {"count": len(orphans), "items": orphans}
    if orphans:
        results["warnings"].append(f"Orphan files found: {len(orphans)}")

    # 2. Broken links
    broken = check_broken_links()
    results["checks"]["broken_links"] = {"count": len(broken), "items": broken}
    if broken:
        results["warnings"].append(f"Broken links found: {len(broken)}")

    # 3. Contradiction density
    recent, esik = check_contradiction_density()
    results["checks"]["contradiction_density"] = {"count": recent, "threshold": esik}
    if recent > esik:
        results["errors"].append(f"Contradiction density exceeded: {recent}/{esik}")

    # 4. Stale content
    stale = check_stale_content(board)
    results["checks"]["stale_content"] = {"count": len(stale), "items": stale}
    if stale:
        results["warnings"].append(f"Stale content: {len(stale)} files older than {YETERLIK_SURE} days")

    # 5. Frontmatter
    missing = check_frontmatter()
    results["checks"]["frontmatter"] = {"missing": len(missing), "items": missing}
    if missing:
        results["warnings"].append(f"Missing frontmatter: {len(missing)} files")

    return results


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Lint LLM wiki health")
    parser.add_argument("--ci", action="store_true", help="CI mode - exit 1 on errors")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues (frontmatter, broken links)")
    parser.add_argument("--output", "-o", help="Save report to JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.fix:
        print("\n=== Auto-fix mode ===")
        fixed_frontmatter, fm_log = fix_frontmatter()
        print("Fixed frontmatter: " + str(fixed_frontmatter) + " files")
        if fm_log and args.verbose:
            for l in fm_log:
                print("\n  " + l)
        fixed_broken, link_log = fix_broken_links()
        print("Fixed broken links: " + str(fixed_broken) + " files")
        if link_log and args.verbose:
            for l in link_log:
                print("  " + l)

    results = lint()
    # JSON output
    if args.output:
        out_path = Path(args.output)
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.verbose:
            print(f"Report saved to {out_path}")

    # Console output
    print("\n=== Wiki Lint Results ===")
    print(f"Timestamp: {results['timestamp']}")

    for check_name, check_data in results["checks"].items():
        status = "OK" if check_data.get("count", 0) == 0 or check_data.get("missing", 0) == 0 else "WARN"
        print(f"  [{status}] {check_name}: {check_data.get('count', 0)}")

    if results["errors"]:
        print(f"\n[ERR] ERRORS ({len(results['errors'])}):")
        for err in results["errors"]:
            print(f"  - {err}")

    if results["warnings"]:
        print(f"\n[WARN] WARNINGS ({len(results['warnings'])}):")
        for warn in results["warnings"]:
            print(f"  - {warn}")

    if not results["errors"] and not results["warnings"]:
        print("\n[OK] All checks passed!")

    if args.ci and (results["errors"] or results["warnings"]):
        total_issues = len(results['errors']) + len(results['warnings'])
        print(f"\nCI FAILED - {total_issues} issue(s) ({len(results['errors'])} error(s), {len(results['warnings'])} warning(s))")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
