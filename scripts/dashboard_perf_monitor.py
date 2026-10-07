#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""P4-4: Dashboard performance monitoring and slow query optimization.

Comprehensive dashboard performance monitor that:
  - Benchmarks all dashboard queries (DB exec time + round-trip time)
  - Runs EXPLAIN ANALYZE to identify slow query plans
  - Tests caching effectiveness
  - Reports performance metrics (response time, query count, cache hit rate)
  - Checks existing indexes

Usage:
    python scripts/dashboard_perf_monitor.py
    python scripts/dashboard_perf_monitor.py --explain  # include EXPLAIN output
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from company_master.db.connection import get_engine
from company_master.dashboard import perf_monitor as pm
from sqlalchemy import text

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "orchestrator"
SLOW_THRESHOLD_MS = 100

# Baseline DB execution times (pre-optimization, from EXPLAIN ANALYZE)
BASELINE = {
    "KPI": 358.69,
    "Sources": 1221.37,
    "Companies_list": 120.03,
    "ILIKE_search": 953.33,
    "Source_IN_filter": 21.38,
    "ASO_count": 0.24,
    "Quality_trend": 54.17,
}

# All dashboard queries (name, sql, params, cache_key)
QUERIES = [
    ("KPI", pm.KPI_QUERY, {}, "kpi"),
    ("Sources", pm.SOURCES_QUERY, {}, "sources"),
    ("Companies_list", pm.COMPANIES_LIST_QUERY, {"min_score": 0, "max_score": 100, "limit": 200}, None),
    ("ILIKE_search", pm.ILIKE_SEARCH_QUERY, {"search": "%dogan%"}, None),
    ("ILIKE_search_optimized", pm.ILIKE_SEARCH_OPTIMIZED_QUERY, {"search": "%dogan%"}, None),
    ("Source_IN_filter", pm.SOURCE_FILTER_QUERY, {"source_name": "ostim.org.tr"}, None),
    ("ASO_count", pm.ASO_COUNT_QUERY, {}, "aso_count"),
    ("Quality_trend", pm.QUALITY_TREND_QUERY, {}, "quality_trend"),
    ("NACE_distribution", pm.NACE_DISTRIBUTION_QUERY, {}, "nace_dist"),
]


def run_benchmark(engine, queries, runs=3, include_explain=False):
    """Benchmark all queries: DB exec time, round-trip time, EXPLAIN plan."""
    results = []
    slow = []
    failed = []
    mon = pm.DashboardPerfMonitor(cache_ttl=300.0)
    mon.page_load_start()

    # Execute each query with profiling (first pass = cache miss)
    for name, sql, params, ck in queries:
        try:
            mon.run_query(name, sql, params, cache_key=ck)
            snap = mon.snapshot()
            last = snap.queries[-1] if snap.queries else {}
            db_ms = last.get("db_ms", 0)
            rt_ms = last.get("roundtrip_ms", 0)
            rows = last.get("rows", 0)
            entry = {"name": name, "db_ms": round(db_ms, 2), "roundtrip_ms": round(rt_ms, 2),
                     "rows": rows, "cache_key": ck}
            if db_ms > SLOW_THRESHOLD_MS:
                entry["status"] = "SLOW"
                slow.append(entry)
            else:
                entry["status"] = "OK"
            results.append(entry)
            print(f"{name}: DB={db_ms:.1f}ms RT={rt_ms:.1f}ms rows={rows} {entry['status']}")
        except Exception as e:
            entry = {"name": name, "db_ms": 0, "roundtrip_ms": 0, "rows": 0,
                     "status": "FAILED", "error": str(e)}
            results.append(entry)
            failed.append(entry)
            print(f"{name}: FAILED - {e}")

    # Reset and test caching: second pass should hit cache
    mon2 = pm.DashboardPerfMonitor(cache_ttl=300.0)
    for name, sql, params, ck in queries:
        if ck:
            mon2.run_query(name, sql, params, cache_key=ck)
    second = mon2.snapshot()

    # Round-trip benchmark (3 runs each, separate connections)
    rt_benchmarks = {}
    for name, sql, params, ck in queries:
        try:
            rts = []
            for _ in range(runs):
                t0 = time.perf_counter()
                with engine.connect() as conn:
                    conn.execute(text(sql), params).fetchall()
                rts.append((time.perf_counter() - t0) * 1000)
            rt_benchmarks[name] = {
                "avg_ms": round(sum(rts) / len(rts), 2),
                "min_ms": round(min(rts), 2),
                "max_ms": round(max(rts), 2),
                "runs": runs,
            }
        except Exception as e:
            rt_benchmarks[name] = {"error": str(e)}

    # EXPLAIN ANALYZE for DB execution time
    explain_results = {}
    if include_explain:
        with engine.connect() as conn:
            for name, sql, params, ck in queries:
                if ck:  # skip cached queries for EXPLAIN
                    continue
                try:
                    explain_sql = "EXPLAIN (ANALYZE, FORMAT JSON) " + sql
                    plan = conn.execute(text(explain_sql), params).one()
                    p = plan[0] if isinstance(plan[0], (list, dict)) else json.loads(plan[0])
                    et = p[0]["Execution Time"] if isinstance(p, list) else p["Execution Time"]
                    explain_results[name] = {"db_exec_ms": round(et, 2)}
                except Exception as e:
                    explain_results[name] = {"error": str(e)}

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_queries": len(results),
        "slow_count": len(slow),
        "failed_count": len(failed),
        "queries": results,
        "roundtrip_benchmark": rt_benchmarks,
        "explain_analyze": explain_results,
        "baseline_db_ms": BASELINE,
        "caching": {
            "cached_query_types": [n for n, s, p, ck in queries if ck],
            "second_load_cache_hits": second.cache_hits,
            "second_load_db_time_ms": round(second.db_time_ms, 2),
        },
        "slow_queries": [{"name": e["name"], "ms": e["db_ms"]} for e in slow],
    }
    return report


def check_indexes(engine):
    """Check existing indexes on dashboard tables."""
    result = {}
    with engine.connect() as conn:
        for table in ["companies", "sources", "source_records"]:
            idxs = [r[0] for r in conn.execute(text(
                "SELECT indexname FROM pg_indexes WHERE tablename = :t ORDER BY indexname"
            ), {"t": table}).fetchall()]
            result[table] = idxs
        counts = {}
        for table in result:
            counts[table] = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    return {"indexes": result, "row_counts": counts}


def main():
    parser = argparse.ArgumentParser(description="P4-4 Dashboard Performance Monitor")
    parser.add_argument("--explain", action="store_true", help="Include EXPLAIN ANALYZE output")
    parser.add_argument("--output", "-o", default=None, help="Output file path")
    args = parser.parse_args()

    engine = get_engine()
    print("=== Dashboard Performance Monitor ===")
    print()

    # Index check
    idx_info = check_indexes(engine)
    print(f"Tables: {idx_info['row_counts']}")
    for table, idxs in idx_info["indexes"].items():
        print(f"  {table}: {len(idxs)} indexes")
    print()

    # Benchmark
    report = run_benchmark(engine, QUERIES, runs=3, include_explain=args.explain)
    report["index_info"] = idx_info

    print()
    print(f"Total queries: {report['total_queries']}")
    print(f"Slow (>{SLOW_THRESHOLD_MS}ms): {report['slow_count']}")
    print(f"Failed: {report['failed_count']}")
    print(f"Cached query types: {report['caching']['cached_query_types']}")
    print(f"Cache hits on 2nd load: {report['caching']['second_load_cache_hits']}")

    out = DATA_DIR / "dashboard_perf_report.json"
    if args.output:
        out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\nReport saved to {out}")


if __name__ == "__main__":
    main()
