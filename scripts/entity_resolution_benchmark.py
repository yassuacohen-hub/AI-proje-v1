#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""P2-4: Entity resolution threshold optimizasyonu (benchmark).

Mevcut threshold: 0.85 (name_fuzzy).
Farkli threshold'lar icin ornneklem uzerinde precision/recall kestirim yapar.

Kullanim:
    python scripts/entity_resolution_benchmark.py
"""
from __future__ import annotations

import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import text  # noqa: E402
from company_master.db.connection import get_engine  # noqa: E402
from company_master.etl.entity_resolution_db import _similarity  # noqa: E402


def main() -> None:
    eng = get_engine()
    with eng.begin() as conn:
        # entity_resolution tablosundaki mevcut sonuclar (ground truth olarak)
        resolved = conn.execute(text("""
            SELECT source_record_id, company_id, match_method, decision
            FROM entity_resolution
        """)).mappings().all()
        print(f"Mevcut resolution kaydi: {len(resolved)}")

        # source_records'tan orneklem al
        src_rows = conn.execute(text("""
            SELECT source_record_id, raw_name, raw_tax_number
            FROM source_records
            WHERE raw_name IS NOT NULL AND raw_name <> ''
            ORDER BY collected_at DESC
            LIMIT 500
        """)).mappings().all()
        print(f"Orneklem: {len(src_rows)} kayit")

        # companies (legal_name)
        companies = conn.execute(text(
            "SELECT company_id, legal_name FROM companies WHERE legal_name IS NOT NULL"
        )).mappings().all()
        name_list = [(c["company_id"], c["legal_name"]) for c in companies]
        print(f"Companies: {len(name_list)} kayit")

    # Farkli threshold'lar icin benchmark
    print("\n--- Threshold Benchmark ---")
    print(f"{'Threshold':<12}{'matched':<10}{'possible':<12}{'new':<10}{'sure_sn':<10}")
    print("-" * 54)

    for threshold in [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
        matched = 0
        possible = 0
        new = 0
        t0 = time.time()
        for row in src_rows:
            name = (row["raw_name"] or "").strip()
            if not name:
                continue
            best = 0.0
            for _, cname in name_list:
                score = _similarity(name, cname)
                if score > best:
                    best = score
            if best >= 0.95:
                matched += 1
            elif best >= threshold:
                possible += 1
            else:
                new += 1
        elapsed = time.time() - t0
        print(f"{threshold:<12.2f}{matched:<10}{possible:<12}{new:<10}{elapsed:<10.2f}")

    # Mevcut threshold (0.85) icin detayli dagilim
    print("\n--- Mevcut threshold (0.85) eslesme dagilimi ---")
    score_buckets = Counter()
    for row in src_rows:
        name = (row["raw_name"] or "").strip()
        if not name:
            continue
        best = max((_similarity(name, cn) for _, cn in name_list), default=0.0)
        bucket = round(best, 2)
        score_buckets[bucket] += 1
    for score in sorted(score_buckets.keys(), reverse=True)[:15]:
        print(f"  {score:.2f}: {score_buckets[score]}")


if __name__ == "__main__":
    main()