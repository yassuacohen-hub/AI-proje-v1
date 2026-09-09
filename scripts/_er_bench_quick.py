# -*- coding: utf-8 -*-
"""P2-4: Entity resolution threshold — hizli analiz (kucuk orneklem)."""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import text  # noqa: E402
from company_master.db.connection import get_engine  # noqa: E402
from company_master.etl.entity_resolution_db import _similarity  # noqa: E402

eng = get_engine()
with eng.begin() as conn:
    # Mevcut resolution istatistikleri
    stats = conn.execute(text("""
        SELECT match_method, decision, count(*) 
        FROM entity_resolution GROUP BY 1,2 ORDER BY 3 DESC
    """)).fetchall()
    print("--- Mevcut entity_resolution dagilimi ---")
    for s in stats:
        print(f"  {s[0]} / {s[1]}: {s[2]}")

    # Kucuk orneklem benchmark (50 source x 500 company)
    src = conn.execute(text("""
        SELECT raw_name FROM source_records 
        WHERE raw_name IS NOT NULL AND raw_name <> '' 
        ORDER BY collected_at DESC LIMIT 50
    """)).fetchall()
    comp = conn.execute(text("""
        SELECT legal_name FROM companies WHERE legal_name IS NOT NULL LIMIT 500
    """)).fetchall()
    names = [c[0] for c in comp]

    print(f"\nBenchmark: {len(src)} source x {len(names)} company")
    print(f"{'Threshold':<12}{'possible_match':<18}{'new_company':<14}{'sure_sn':<10}")
    print("-" * 54)
    for thr in [0.75, 0.80, 0.85, 0.90, 0.95]:
        possible = new = 0
        t0 = time.time()
        for r in src:
            name = (r[0] or "").strip()
            if not name:
                continue
            best = max((_similarity(name, cn) for cn in names), default=0.0)
            if best >= 0.95:
                pass  # exact-ish
            elif best >= thr:
                possible += 1
            else:
                new += 1
        print(f"{thr:<12.2f}{possible:<18}{new:<14}{time.time()-t0:<10.2f}")