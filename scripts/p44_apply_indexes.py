#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""P4-4: Apply missing performance indexes and update table statistics."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from company_master.db.connection import get_engine
from sqlalchemy import text


INDEXES = [
    (
        "idx_source_records_covering",
        "CREATE INDEX IF NOT EXISTS idx_source_records_covering "
        "ON source_records(source_id) INCLUDE (source_record_id, collected_at)",
    ),
    (
        "idx_companies_source_record_score",
        "CREATE INDEX IF NOT EXISTS idx_companies_source_record_score "
        "ON companies(source_record_id, data_quality_score DESC) "
        "WHERE is_ankara = TRUE AND is_osb_member = TRUE",
    ),
    (
        "idx_companies_nace",
        "CREATE INDEX IF NOT EXISTS idx_companies_nace "
        "ON companies(nace_code) WHERE is_ankara = TRUE AND is_osb_member = TRUE",
    ),
]


def run_analyze():
    engine = get_engine()
    tables = ["companies", "sources", "source_records"]
    with engine.connect() as conn:
        for t in tables:
            conn.execute(text(f"ANALYZE {t}"))
            print(f"  ANALYZE {t} OK")
        conn.commit()


def main():
    engine = get_engine()
    print("=== P4-4 Index Optimization ===\n")

    # Show existing indexes
    with engine.connect() as conn:
        existing = set()
        for r in conn.execute(text(
            "SELECT indexname FROM pg_indexes WHERE tablename IN ('companies','sources','source_records')"
        )).fetchall():
            existing.add(r[0])
        print(f"Existing indexes before: {len(existing)}")
        for idx in sorted(existing):
            print(f"  - {idx}")

    applied = []
    skipped = []
    with engine.connect() as conn:
        for name, ddl in INDEXES:
            if name in existing:
                skipped.append(name)
                print(f"\nSKIP (already exists): {name}")
                continue
            t0 = time.perf_counter()
            try:
                conn.execute(text(ddl))
                conn.commit()
                elapsed = (time.perf_counter() - t0) * 1000
                applied.append({"name": name, "ms": round(elapsed, 1)})
                print(f"\nCREATED: {name} ({elapsed:.0f} ms)")
            except Exception as e:
                skipped.append(name)
                print(f"\nERROR creating {name}: {e}")

    print("\n=== Running ANALYZE on key tables ===")
    run_analyze()

    # Verify
    with engine.connect() as conn:
        after = set()
        for r in conn.execute(text(
            "SELECT indexname FROM pg_indexes WHERE tablename IN ('companies','sources','source_records')"
        )).fetchall():
            after.add(r[0])
        print(f"\nTotal indexes after: {len(after)}")

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "indexes_applied": applied,
        "indexes_skipped": skipped,
        "indexes_total_before": len(existing),
        "indexes_total_after": len(after),
        "analyze_run": True,
    }

    out_path = Path(__file__).resolve().parents[1] / "data" / "orchestrator" / "p44_index_optimization.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        __import__("json").dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nIndex optimization report saved to {out_path}")
    return report


if __name__ == "__main__":
    main()
