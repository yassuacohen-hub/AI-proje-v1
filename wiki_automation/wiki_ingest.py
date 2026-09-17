#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM Wiki - Agent Output Ingestion Script
----------------------------------------
Bu script, harici ajanların workspace/external/{agent_id}/output/ dizinindeki
çıktı dosyalarını okur ve AI proje v1/V10/wiki/tasks/ dizinine wiki sayfaları
olarak dönüştürür. Ayrıca çelişkileri tespit eder ve index/log dosyalarını günceller.

Kullanım:
    python wiki_ingest.py                    # Tüm yeni çıktıları işle
    python wiki_ingest.py --agent copilot    # Sadece copilot'ın çıktılarını işle
    python wiki_ingest.py --dry-run          # Değişiklik yapmadan göster
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Proje kök dizini
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_EXTERNAL = PROJECT_ROOT / "workspace" / "external"
WIKI_ROOT = PROJECT_ROOT / "AI proje v1" / "V10" / "wiki"
WIKI_TASKS = WIKI_ROOT / "tasks"
WIKI_AGENTS = WIKI_ROOT / "agents"
WIKI_INDEX = WIKI_ROOT / "00_index.md"
WIKI_LOG = WIKI_ROOT / "00_log.md"
CONTRADICTIONS = WIKI_ROOT / "contradictions.md"

# Wiki link pattern
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]]*)?(?:\|[^\]]*)?\]\]")

# Ajan tipleri (external agent workspace'leri)
AGENT_TYPES = {
    "claude_code", "copilot", "cursor_grok", "harici_ajan"
}


def ensure_directories() -> None:
    """Gerekli klasörlerin varlığını kontrol et, yoksa oluştur."""
    for directory in [WIKI_TASKS, WIKI_AGENTS]:
        directory.mkdir(parents=True, exist_ok=True)


def frontmatter_extract(text: str) -> Tuple[Dict[str, str], str]:
    """
    Markdown metninden YAML frontmatter'ını ayır.
    Returns: (frontmatter_dict, body_content)
    """
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
    """Frontmatter dict'inden YAML string'i oluştur."""
    if not meta:
        return ""
    lines = ["---"]
    for key, value in meta.items():
        lines.append(f"{key}: {value}")
    lines.append("---\n")
    return "\n".join(lines)


def slugify(text: str) -> str:
    """Dosya adı için güvenli slug oluştur."""
    turkish_map = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'C', 'Ğ': 'G', 'I': 'İ', 'Ö': 'O', 'Ş': 'Ş', 'Ü': 'Ü'
    }
    for tr, en in turkish_map.items():
        text = text.replace(tr, en)
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text or "untitled"


def extract_wiki_links(text: str) -> Set[str]:
    """Metinden [[wiki link]] formatındaki linkleri çıkar."""
    return set(WIKILINK_RE.findall(text))


def detect_contradictions(new_content: str, existing_content: str) -> List[Tuple[str, str]]:
    """
    İki içerik arasında çelişki tespit et.
    Basit bir yaklaşım: olumsuzlama ifadelerini ara.
    Daha gelişmiş bir NLP modeli kullanılabilir.
    """
    contradictions = []
    negation_patterns = [
        r'\b(değil|değildir|yanlış|yanılsın|yanlış olduğu|yanlış olduğunu)\b',
        r'\b(not|is not|does not|false|incorrect)\b',
        r'\b(yanıt|yanıtlamıyor|yanıt vermiyor)\b',
        r'\b(yanlış anlaşılma|yanılsı|yanılsı olduğu)\b'
    ]

    new_sentences = re.split(r'[.!?]+', new_content)
    existing_sentences = re.split(r'[.!?]+', existing_content)

    for new_sent in new_sentences:
        new_sent = new_sent.strip()
        if not new_sent:
            continue
        has_negation = any(re.search(pattern, new_sent, re.IGNORECASE)
                           for pattern in negation_patterns)
        if not has_negation:
            continue

        positive_sent = re.sub(r'\b(değil|değildir|yanlış|yanılsın|not|is not|does not|false|incorrect)\b', '', new_sent, flags=re.IGNORECASE).strip()
        positive_sent = re.sub(r'\s+', ' ', positive_sent)
        if positive_sent and len(positive_sent) > 10:
            for exist_sent in existing_sentences:
                exist_sent = exist_sent.strip()
                if exist_sent and len(exist_sent) > 10:
                    new_words = set(positive_sent.lower().split())
                    exist_words = set(exist_sent.lower().split())
                    if new_words and exist_words:
                        intersection = len(new_words & exist_words)
                        union = len(new_words | exist_words)
                        similarity = intersection / union if union > 0 else 0
                        if similarity > 0.5:
                            contradictions.append((new_sent, exist_sent))
    return contradictions

def process_agent_output(agent_id: str, dry_run: bool = False) -> Tuple[int, int, List[str]]:
    agent_output_dir = WORKSPACE_EXTERNAL / agent_id / "output"
    if not agent_output_dir.exists():
        return 0, 0, [f"Agent output directory not found: {agent_output_dir}"]
    processed = 0
    skipped = 0
    errors = []
    for md_file in agent_output_dir.glob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            task_id = md_file.stem
            if '_' in task_id:
                task_id = task_id.split('_')[0]
            wiki_task_file = WIKI_TASKS / f"{task_id}.md"
            meta = {
                "agent": agent_id,
                "source": str(md_file.relative_to(PROJECT_ROOT)),
                "ingested": datetime.now(timezone.utc).isoformat(),
                "type": "task_output"
            }
            existing_content = ""
            existing_meta = {}
            existing_body = ""
            if wiki_task_file.exists():
                existing_content = wiki_task_file.read_text(encoding="utf-8")
                existing_meta, existing_body = frontmatter_extract(existing_content)
                meta.update({k: v for k, v in existing_meta.items() if k not in ["agent", "source", "ingested"]})
            new_body = f"""{content}
*Bu içerik {agent_id} tarafından {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC'de ingest edildi.*
"""
            new_content = frontmatter_create(meta) + new_body
            contradictions = []
            if existing_content:
                contradictions = detect_contradictions(new_body, existing_body)
            if dry_run:
                print(f"[DRY-RUN] Would process: {md_file} -> {wiki_task_file}")
                if contradictions:
                    print(f"  [DRY-RUN] Contradictions: {len(contradictions)}")
                processed += 1
            else:
                wiki_task_file.write_text(new_content, encoding="utf-8")
                processed += 1
                if contradictions:
                    with open(CONTRADICTIONS, "a", encoding="utf-8") as f:
                        f.write(f"\n## Contradictions at {datetime.now(timezone.utc).isoformat()}\n")
                        f.write(f"**File:** {md_file.name} -> {wiki_task_file.name}\n")
                        for s1, s2 in contradictions:
                            f.write(f"- New: {s1}\n- Existing: {s2}\n")
                        f.write("\n---\n")
        except Exception as e:
            errors.append(f"Error processing {md_file}: {str(e)}")
            skipped += 1
    return processed, skipped, errors


def update_wiki_log(agent_id: str, processed: int, skipped: int, errors: List[str]) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    log_entry = f"## [{timestamp}] wiki_ingest - {agent_id}\n- Processed: {processed} files\n- Skipped: {skipped} files\n- Errors: {len(errors)}\n"
    if errors:
        log_entry += "- Error details:\n"
        for err in errors:
            log_entry += f"  - {err}\n"
    log_entry += "\n---\n\n"
    if WIKI_LOG.exists():
        current_log = WIKI_LOG.read_text(encoding="utf-8")
        new_log = log_entry + current_log
    else:
        new_log = "# Wiki Ingestion Log\n\n---\n\n" + log_entry
    WIKI_LOG.write_text(new_log, encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest agent outputs into LLM wiki")
    parser.add_argument("--agent", help="Specific agent to process (e.g., copilot)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    ensure_directories()
    if args.agent:
        agents_to_process = [args.agent] if args.agent in AGENT_TYPES else []
        if not agents_to_process:
            print(f"Error: Unknown agent '{args.agent}'. Available: {', '.join(sorted(AGENT_TYPES))}")
            return 1
    else:
        agents_to_process = []
        if WORKSPACE_EXTERNAL.exists():
            for agent_dir in WORKSPACE_EXTERNAL.iterdir():
                if agent_dir.is_dir() and agent_dir.name in AGENT_TYPES:
                    agents_to_process.append(agent_dir.name)
    if not agents_to_process:
        print("No agent workspaces found to process.")
        return 0
    total_processed = 0
    total_skipped = 0
    total_errors = []
    for agent_id in agents_to_process:
        if args.verbose:
            print(f"Processing agent: {agent_id}")
        processed, skipped, errors = process_agent_output(agent_id, args.dry_run)
        total_processed += processed
        total_skipped += skipped
        total_errors.extend(errors)
        if not args.dry_run:
            update_wiki_log(agent_id, processed, skipped, errors)
        if args.verbose:
            print(f"  Processed: {processed}, Skipped: {skipped}, Errors: {len(errors)}")
    print(f"\n=== Wiki Ingestion Summary ===")
    print(f"Agents processed: {len(agents_to_process)}")
    print(f"Files processed: {total_processed}")
    print(f"Files skipped: {total_skipped}")
    print(f"Errors: {len(total_errors)}")
    if total_errors and not args.dry_run:
        print("\nErrors:")
        for err in total_errors[:5]:
            print(f"  - {err}")
        if len(total_errors) > 5:
            print(f"  ... and {len(total_errors) - 5} more")
    if not args.dry_run:
        print(f"\nWiki updated: {WIKI_ROOT}")
        print(f"Log updated: {WIKI_LOG}")
        if total_errors:
            print(f"Contradictions logged: {CONTRADICTIONS}")
    return 0 if len(total_errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
