# -*- coding: utf-8 -*-
"""Apify Webhook DLQ Monitor — Dead-Letter Queue analysis ve yönetim.

DLQ girdilerini okur, istatistik üretir, hata türlerine göre filtreler
ve raporlar oluşturur. Apify webhook alıcısının DLQ dosyasına (jsonl)
bağlanır.

Kullanım:
    python -m company_master.intelligence.job_intelligence.pipeline.dlq_monitor [--filter auth_error] [--verbose]
"""
from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[5]
DLQ_PATH = ROOT / "data" / "orchestrator" / "apify_webhook_dlq.jsonl"

ERROR_COLORS: dict[str, str] = {
    "auth_error": "🔴",
    "validation_error": "🟠",
    "rate_limit": "🟡",
    "timeout": "🟡",
    "network_error": "🔵",
}


class DLQEntry:
    """Tek bir DLQ kaydı."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.timestamp: str = data.get("timestamp", "")
        self.error_type: str = data.get("error_type", "unknown")
        self.error: str = data.get("error", "")
        self.payload: dict[str, Any] = data.get("payload", {})

    @property
    def actor_run_id(self) -> str:
        return self.payload.get("actorRunId", "")

    @property
    def event_type(self) -> str:
        return self.payload.get("eventType", "")

    @property
    def actor_id(self) -> str:
        return self.payload.get("actorId", self.payload.get("actorId", ""))

    def age_hours(self, reference: datetime | None = None) -> float | None:
        try:
            ts = datetime.fromisoformat(self.timestamp)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            ref = reference or datetime.now(timezone.utc)
            delta = ref - ts
            return round(delta.total_seconds() / 3600, 2)
        except (ValueError, TypeError):
            return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "error_type": self.error_type,
            "error": self.error,
            "payload": self.payload,
            "actor_run_id": self.actor_run_id,
            "event_type": self.event_type,
            "actor_id": self.actor_id,
            "age_hours": self.age_hours(),
        }


class ApifyDLQMonitor:
    """Apify Webhook DLQ monitor ve analiz aracı."""

    def __init__(self, dlq_path: Path | str | None = None) -> None:
        self.dlq_path = Path(dlq_path) if dlq_path else DLQ_PATH
        self._entries: list[DLQEntry] | None = None

    @property
    def entries(self) -> list[DLQEntry]:
        if self._entries is None:
            self._entries = self._load_entries()
        return self._entries

    def _load_entries(self) -> list[DLQEntry]:
        if not self.dlq_path.exists():
            logger.info("DLQ dosyası bulunamadı: %s", self.dlq_path)
            return []
        entries: list[DLQEntry] = []
        for line in self.dlq_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                entries.append(DLQEntry(data))
            except json.JSONDecodeError:
                logger.warning("DLQ satırı atlandı (geçersiz JSON): %s", line[:100])
        return entries

    def refresh(self) -> None:
        self._entries = None

    def total_count(self) -> int:
        return len(self.entries)

    def error_type_counts(self) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for entry in self.entries:
            counter[entry.error_type] += 1
        return dict(counter)

    def entries_by_error_type(self, error_type: str) -> list[DLQEntry]:
        return [e for e in self.entries if e.error_type == error_type]

    def entries_by_actor(self, actor_id: str) -> list[DLQEntry]:
        return [e for e in self.entries if e.actor_id == actor_id]

    def recent_entries(self, hours: int = 24, reference: datetime | None = None) -> list[DLQEntry]:
        cutoff = (reference or datetime.now(timezone.utc)).timestamp() - hours * 3600
        result: list[DLQEntry] = []
        for entry in self.entries:
            try:
                ts = datetime.fromisoformat(entry.timestamp).timestamp()
                if ts >= cutoff:
                    result.append(entry)
            except (ValueError, TypeError):
                continue
        return result

    def summary(self) -> dict[str, Any]:
        counts = self.error_type_counts()
        timestamps = []
        for entry in self.entries:
            try:
                timestamps.append(datetime.fromisoformat(entry.timestamp))
            except (ValueError, TypeError):
                continue
        timestamps.sort()
        return {
            "total": self.total_count(),
            "error_types": counts,
            "first_seen": timestamps[0].isoformat() if timestamps else None,
            "last_seen": timestamps[-1].isoformat() if timestamps else None,
            "unique_actors": len(set(e.actor_id for e in self.entries if e.actor_id)),
            "unique_event_types": sorted(set(e.event_type for e in self.entries if e.event_type)),
            "auth_errors": counts.get("auth_error", 0),
            "validation_errors": counts.get("validation_error", 0),
        }

    def retry_entry(self, index: int) -> dict[str, Any]:
        if index < 0 or index >= len(self.entries):
            return {"success": False, "error": f"Index out of range: {index}"}
        entry = self.entries[index]
        try:
            from scripts.apify_webhook_receiver import ApifyWebhookReceiver
            receiver = ApifyWebhookReceiver()
            result = receiver._process_event(entry.payload) if hasattr(receiver, "_process_event") else {"status": "queued"}
            return {"success": True, "index": index, "actor_run_id": entry.actor_run_id, "result": result}
        except Exception as exc:
            return {"success": False, "index": index, "error": str(exc)}

    def clear_dlq(self) -> int:
        if self.dlq_path.exists():
            count = len(self.entries)
            self.dlq_path.write_text("", encoding="utf-8")
            self.refresh()
            return count
        return 0

    def format_report(self, verbose: bool = False) -> str:
        lines: list[str] = []
        summary = self.summary()
        lines.append("=" * 60)
        lines.append("Apify Webhook DLQ Raporu")
        lines.append("=" * 60)
        lines.append(f"Toplam DLQ Kaydı : {summary['total']}")
        lines.append(f"İlkel Kayıt      : {summary['first_seen'] or '—'}")
        lines.append(f"Son Kayıt        : {summary['last_seen'] or '—'}")
        lines.append(f"Benzersiz Aktör  : {summary['unique_actors']}")
        lines.append("")
        lines.append("--- Hata Türleri ---")
        for etype, count in summary["error_types"].items():
            icon = ERROR_COLORS.get(etype, "⚪")
            lines.append(f"  {icon} {etype}: {count}")
        lines.append("")
        lines.append("--- Özet ---")
        lines.append(f"  🔴 Auth Hata   : {summary['auth_errors']}")
        lines.append(f"  🟠 Doğrulama  : {summary['validation_errors']}")
        lines.append("")
        if verbose:
            lines.append("--- Detay Kayıtları ---")
            for i, entry in enumerate(self.entries):
                d = entry.to_dict()
                lines.append(f"[{i}] {d['timestamp'][:19]} | {d['error_type']} | {d['error']}")
                lines.append(f"    Aktör: {d['actor_id']} | Run: {d['actor_run_id']} | Event: {d['event_type']}")
                lines.append(f"    Yaş: {d['age_hours']:.1f} saat" if d['age_hours'] is not None else "    Yaş: —")
        lines.append("=" * 60)
        return "\n".join(lines)


def main() -> None:
    import argparse
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description="Apify Webhook DLQ Monitor")
    parser.add_argument("--filter", dest="filter_type", default=None, help="Hata türüne göre filtrele")
    parser.add_argument("--verbose", action="store_true", help="Detaylı çıktı")
    parser.add_argument("--recent-hours", type=int, default=None, help="Son N saatteki kayıtlar")
    parser.add_argument("--clear", action="store_true", help="DLQ'yı temizle")
    parser.add_argument("--retry-index", type=int, default=None, help="Tekrar dene (index)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    monitor = ApifyDLQMonitor()

    if args.clear:
        count = monitor.clear_dlq()
        print(f"DLQ temizlendi: {count} kayıt silindi.")
        return

    if args.retry_index is not None:
        result = monitor.retry_entry(args.retry_index)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.filter_type:
        entries = monitor.entries_by_error_type(args.filter_type)
        print(f"\n🔍 Filtre: {args.filter_type} ({len(entries)} kayıt)")
        for i, entry in enumerate(entries):
            d = entry.to_dict()
            print(f"  [{i}] {d['timestamp'][:19]} | {d['error']}")
        return

    if args.recent_hours:
        entries = monitor.recent_entries(args.recent_hours)
        print(f"\n⏰ Son {args.recent_hours} saat: {len(entries)} kayıt")
        for entry in entries:
            d = entry.to_dict()
            print(f"  {d['timestamp'][:19]} | {d['error_type']} | {d['error']}")
        return

    print(monitor.format_report(verbose=args.verbose))


if __name__ == "__main__":
    main()
