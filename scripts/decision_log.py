"""Decision Log mekanizmasi - kararlari JSONL formatinda kaydeder.

Kullanim:
    from scripts.decision_log import read_decisions, log_decision, search_decisions

Dosya:
    data/orchestrator/decision_log.jsonl
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DECISION_LOG = ROOT / "data" / "orchestrator" / "decision_log.jsonl"


def _ensure_file() -> None:
    """Decision log dosyasini ve dizinini olusturur."""
    DECISION_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not DECISION_LOG.exists():
        DECISION_LOG.write_text("", encoding="utf-8")


def _atomic_write_all(entries: list[dict[str, Any]]) -> None:
    """Tum kayitlari atomik olarak yazar (UTF-8)."""
    tmp = DECISION_LOG.parent / f".{DECISION_LOG.name}.{os.getpid()}.tmp"
    try:
        tmp.write_text(
            "\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n",
            encoding="utf-8",
        )
        os.replace(tmp, DECISION_LOG)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def read_decisions(limit: int = 50) -> list[dict[str, Any]]:
    """Decision log dosyasini okur, son limit kaydi dondurur.

    Dosya yoksa bos liste dondurur.
    """
    _ensure_file()
    entries: list[dict[str, Any]] = []
    for line in DECISION_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries[-limit:] if limit > 0 else entries


def log_decision(
    title: str,
    decision: str,
    decider: str,
    reason: str,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Yeni karar kaydini sona ekler (UTF-8, atomik yazma).

    Args:
        title: Kararin basligi.
        decision: Karar degeri (orn: accepted, rejected, deferred).
        decider: Karari veren taraf.
        reason: Kararin gerekceyi.
        tags: Ilgili etiketler.

    Returns:
        Olusturulan karar kaydi dict'i.
    """
    entry: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "title": title,
        "decision": decision,
        "decider": decider,
        "reason": reason,
        "tags": tags or [],
    }
    existing = read_decisions(limit=0)
    existing.append(entry)
    _atomic_write_all(existing)
    return entry


def search_decisions(query: str) -> list[dict[str, Any]]:
    """title/reason/tags icerisinde basit metin aramasi yapar.

    Arama case-insensitive ve kelime kismi eslesme yapar.
    """
    if not query:
        return []
    q = query.lower()
    results: list[dict[str, Any]] = []
    for entry in read_decisions(limit=0):
        title = str(entry.get("title", "")).lower()
        reason = str(entry.get("reason", "")).lower()
        raw_tags = entry.get("tags", [])
        if not isinstance(raw_tags, list):
            raw_tags = [str(t) for t in raw_tags]
        tags_str = " ".join(str(t).lower() for t in raw_tags)
        if q in title or q in reason or q in tags_str:
            results.append(entry)
    return results
