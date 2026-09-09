#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""P4-4: Comprehensive dashboard performance benchmark."""
from __future__ import annotations
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from company_master.db.connection import get_engine
from company_master.dashboard import perf_monitor as pm
from sqlalchemy import text

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "orchestrator"
BASELINE = {"KPI": 358.69, "Sources": 1221.37, "Companies_list": 120.03, "ILIKE_search": 953.33, "ASO_count": 0.24, "Quality_trend": 54.17}


QUERIES = {
    "KPI": (pm.KPI_QUERY, {}, "kpi"),
    "Sources": (pm.SOURCES_QUERY, {}, "sources"),
    "Companies_list": (pm.COMPANIES_LIST_QUERY, {"min_score": 0, "max_score": 100, "limit": 200}, None),
    "ILIKE_search": (pm.ILIKE_SEARCH_QUERY, {"search": "%dogan%"}, None),
    "Source_IN_filter": (pm.SOURCE_FILTER_QUERY, {"source_name": "ostim.org.tr"}, None),
    "ASO_count": (pm.ASO_COUNT_QUERY, {}, "aso_count"),
    "Quality_trend": (pm.QUALITY_TREND_QUERY, {}, "quality_trend"),
    "NACE_distribution": (pm.NACE_DISTRIBUTION_QUERY, {}, "nace_dist"),
}


def explain_analyze(engine, sql, params):
    """Run EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) and extract execution time."""
    explain_sql = "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql
    t0 = time.perf_counter()
    with engine.connect() as conn:
        plan = conn.execute(text(explain_sql), params).one()
        roundtrip_ms = (time.perf_counter() - t0) * 1000
    # SQLAlchemy may return the JSON as a parsed list/dict already
    if isinstance(plan[0], (list, dict)):
        plan_str = plan[0]
    else:
        plan_str = json.loads(plan[0])
    exec_time = plan_str[0]["Execution Time"] if isinstance(plan_str, list) else plan_str["Execution Time"]
    return {"db_exec_ms": round(exec_time, 2), "roundtrip_ms": round(roundtrip_ms, 2)}


def benchmark_roundtrip(engine, sql, params, runs=3):
    """Run query N times, return avg round-trip time."""
    times = []
    rows = []
    for i in range(runs):
        t0 = time.perf_counter()
        with engine.connect() as conn:
            rows = conn.execute(text(sql), params).mappings().all()
        elapsed = (time.perf_counter() - t0) * 1000
        times.append(elapsed)
    return {
        "avg_ms": round(sum(times) / len(times), 2),
        "min_ms": round(min(times), 2),
        "max_ms": round(max(times), 2),
        "runs": runs,
        "rows": len(rows),
    }


def test_caching():
    """Test cache effectiveness for dashboard page loads."""
    mon = pm.DashboardPerfMonitor(cache_ttl=300.0)
    mon.page_load_start()
    for name, (sql, params, ck) in QUERIES.items():
        if ck:
            mon.run_query(name, sql, params, cache_key=ck)
        else:
            mon.run_query(name, sql, params)
    first = mon.snapshot()
    for name, (sql, params, ck) in QUERIES.items():
        if ck:
            mon.run_query(name, sql, params, cache_key=ck)
    second = mon.snapshot()
    cached_types = [n for n, (s, p, ck) in QUERIES.items() if ck]
    return {
        "first_load": {
            "query_count": first.query_count,
            "db_time_ms": first.db_time_ms,
            "roundtrip_ms": first.roundtrip_ms,
            "cache_hits": first.cache_hits,
            "cache_misses": first.cache_misses,
            "cache_hit_rate": first.cache_hit_rate,
        },
        "second_load": {
            "query_count": second.query_count - first.query_count,
            "db_time_ms": round(second.db_time_ms - first.db_time_ms, 2),
            "roundtrip_ms": round(second.roundtrip_ms - first.roundtrip_ms, 2),
            "cache_hits": second.cache_hits - first.cache_hits,
            "cache_misses": second.cache_misses - first.cache_misses,
            "cache_hit_rate": second.cache_hit_rate,
        },
        "cached_query_types": cached_types,
    }


def main():
    engine = get_engine()
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "task": "Dashboard performans izleme ve slow query optimization",
        "database": "PostgreSQL (Supabase)",
        "total_companies": 14000,
        "queries": {},
    }

    print("=== P4-4: Dashboard Performance Benchmark ===")
    print()

    # Warm up caches
    for name, (sql, params, ck) in QUERIES.items():
        with engine.connect() as conn:
            conn.execute(text(sql), params).fetchall()

    for name, (sql, params, ck) in QUERIES.items():
        print(f"--- {name} ---")
        # EXPLAIN ANALYZE (DB execution time)
        try:
            ea = explain_analyze(engine, sql, params)
            print(f"  DB exec: {ea['db_exec_ms']} ms | roundtrip: {ea['roundtrip_ms']} ms")
            baseline = BASELINE.get(name)
            improvement = None
            if baseline:
                improvement = round((baseline - ea["db_exec_ms"]) / baseline * 100, 1)
                print(f"  DB improvement: {baseline} -> {ea['db_exec_ms']} ms ({improvement:+.1f}%)")
            results["queries"][name] = {
                "db_exec_ms": ea["db_exec_ms"],
                "roundtrip_ms": ea["roundtrip_ms"],
                "baseline_db_ms": baseline,
                "improvement_pct": improvement,
            }
        except Exception as e:
            print(f"  EXPLAIN ANALYZE ERROR: {e}")
            results["queries"][name] = {"explain_analyze_error": str(e)}

        # Round-trip benchmark (3 runs)
        try:
            rt = benchmark_roundtrip(engine, sql, params)
            print(f"  Round-trip avg: {rt['avg_ms']} ms (rows={rt['rows']})")
            results["queries"][name]["roundtrip_benchmark"] = rt
        except Exception as e:
            print(f"  Round-trip ERROR: {e}")
            results["queries"][name]["roundtrip_error"] = str(e)
        print()

    # Caching test
    print("=== Caching Test ===")
    caching = test_caching()
    results["caching"] = caching
    print(f"  First load: {caching['first_load']['query_count']} queries, DB={caching['first_load']['db_time_ms']}ms, cache_hit_rate={caching['first_load']['cache_hit_rate']}")
    print(f"  Second load: {caching['second_load']['query_count']} queries, cache_hits={caching['second_load']['cache_hits']}")
    print(f"  Cached types: {caching['cached_query_types']}")

    # Summary
    slow_db = [n for n, r in results["queries"].items() if "db_exec_ms" in r and r["db_exec_ms"] > 100]
    slow_rt = [n for n, r in results["queries"].items() if "roundtrip_benchmark" in r and r["roundtrip_benchmark"]["avg_ms"] > 100]
    avg_improvement = round(
        sum(r.get("improvement_pct", 0) or 0 for r in results["queries"].values() if "improvement_pct" in r and r["improvement_pct"]), 1
    )
    results["summary"] = {
        "total_queries": len(QUERIES),
        "slow_db_queries": slow_db,
        "slow_roundtrip_queries": slow_rt,
        "avg_db_improvement_pct": avg_improvement,
        "cache_first_load_db_ms": caching["first_load"]["db_time_ms"],
        "cache_second_load_db_ms": caching["second_load"]["db_time_ms"],
    }
    print()
    print(f"Slow DB queries: {slow_db}")
    print(f"Slow round-trip queries: {slow_rt}")

    out = DATA_DIR / "p44_benchmark_full.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"Benchmark saved to {out}")
    return results


if __name__ == "__main__":
    main()

