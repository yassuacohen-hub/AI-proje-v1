#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""P4-4: Final benchmark and report generator."""
from __future__ import annotations
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from company_master.db.connection import get_engine
from company_master.dashboard import perf_monitor as pm
from sqlalchemy import text

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "orchestrator"
BASELINE = {"KPI": 358.69, "Sources": 1221.37, "Companies_list": 120.03, "ILIKE_search": 953.33, "Source_IN_filter": 21.38, "ASO_count": 0.24, "Quality_trend": 54.17}

QUERIES = {
    "KPI": ("KPI", pm.KPI_QUERY, {}, "kpi"),
    "Sources": ("Sources", pm.SOURCES_QUERY, {}, "sources"),
    "Companies_list": ("Companies_list", pm.COMPANIES_LIST_QUERY, {"min_score": 0, "max_score": 100, "limit": 200}, None),
    "ILIKE_search": ("ILIKE_search", pm.ILIKE_SEARCH_QUERY, {"search": "%dogan%"}, None),
    "Source_IN_filter": ("Source_IN_filter", pm.SOURCE_FILTER_QUERY, {"source_name": "ostim.org.tr"}, None),
    "ASO_count": ("ASO_count", pm.ASO_COUNT_QUERY, {}, "aso_count"),
    "Quality_trend": ("Quality_trend", pm.QUALITY_TREND_QUERY, {}, "quality_trend"),
    "NACE_distribution": ("NACE_distribution", pm.NACE_DISTRIBUTION_QUERY, {}, "nace_dist"),
}

ILIKE_OPTIMIZED = {
    "name": "ILIKE_search_optimized",
    "sql": "SELECT c.legal_name, c.trade_name, c.website_domain, c.primary_phone, c.primary_email, c.tax_number, c.vergi_no, c.nace_code, c.data_quality_score FROM companies c WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE AND c.search_text ILIKE :s ORDER BY c.data_quality_score DESC LIMIT 50",
    "params": {"s": "%dogan%"},
}

def explain_analyze(engine, sql, params):
    explain_sql = "EXPLAIN (ANALYZE, FORMAT JSON) " + sql
    t0 = time.perf_counter()
    with engine.connect() as conn:
        plan = conn.execute(text(explain_sql), params).one()
        roundtrip_ms = (time.perf_counter() - t0) * 1000
    p = plan[0] if isinstance(plan[0], (list, dict)) else json.loads(plan[0])
    exec_time = p[0]["Execution Time"] if isinstance(p, list) else p["Execution Time"]
    return {"db_exec_ms": round(exec_time, 2), "roundtrip_ms": round(roundtrip_ms, 2)}


def bench_roundtrip(engine, sql, params, runs=3):
    times = []
    rows = 0
    for i in range(runs):
        t0 = time.perf_counter()
        with engine.connect() as conn:
            rows = len(conn.execute(text(sql), params).mappings().all())
        times.append((time.perf_counter() - t0) * 1000)
    return {"avg_ms": round(sum(times)/len(times), 2), "min_ms": round(min(times), 2), "max_ms": round(max(times), 2), "runs": runs, "rows": rows}


def check_indexes(engine):
    result = {}
    for table in ["companies", "sources", "source_records"]:
        idxs = [r[0] for r in engine.connect().execute(text("SELECT indexname FROM pg_indexes WHERE tablename = :t ORDER BY indexname"), {"t": table}).fetchall()]
        result[table] = idxs
    return result


def main():
    engine = get_engine()
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "task_id": "P4-4",
        "task": "Dashboard performans izleme ve slow query optimization",
        "database": "PostgreSQL (Supabase) via DATABASE_URL",
    }
    print("=== P4-4: Final Dashboard Performance Benchmark ===")
    print()
    # Warm up
    for label, sql, params, ck in QUERIES.values():
        pass
    index_info = check_indexes(engine)
    report["indexes"] = index_info
    report["total_companies"] = engine.connect().execute(text("SELECT COUNT(*) FROM companies")).scalar()
    report["queries"] = {}
    # Benchmark each query
    for label, sql, params, ck in QUERIES.values():
        name = label
        print(f"--- {name} ---")
        qdata = {}
        try:
            ea = explain_analyze(engine, sql, params)
            qdata["db_exec_ms"] = ea["db_exec_ms"]
            qdata["roundtrip_ms"] = ea["roundtrip_ms"]
            baseline = BASELINE.get(name)
            if baseline and name in ("KPI", "Sources", "Companies_list", "ILIKE_search", "Source_IN_filter", "ASO_count", "Quality_trend"):
                imp = round((baseline - ea["db_exec_ms"]) / baseline * 100, 1)
                qdata["baseline_db_ms"] = baseline
                qdata["db_improvement_pct"] = imp
                print(f"  DB: {baseline}ms -> {ea['db_exec_ms']}ms ({imp:+.1f}%)")
            else:
                print(f"  DB: {ea['db_exec_ms']}ms")
        except Exception as e:
            qdata["explain_error"] = str(e)
            print(f"  Explain ERROR: {e}")
        try:
            rt = bench_roundtrip(engine, sql, params)
            qdata["roundtrip_benchmark"] = rt
            print(f"  Round-trip avg: {rt['avg_ms']}ms (rows={rt['rows']})")
        except Exception as e:
            qdata["bench_error"] = str(e)
            print(f"  Bench ERROR: {e}")
        qdata["cache_key"] = ck
        report["queries"][name] = qdata
        print()
    # Optimized ILIKE search
    print("--- ILIKE_search_optimized (search_text) ---")
    try:
        ea = explain_analyze(engine, ILIKE_OPTIMIZED["sql"], ILIKE_OPTIMIZED["params"])
        rt = bench_roundtrip(engine, ILIKE_OPTIMIZED["sql"], ILIKE_OPTIMIZED["params"])
        opt = {"db_exec_ms": ea["db_exec_ms"], "roundtrip_ms": ea["roundtrip_ms"], "roundtrip_benchmark": rt, "baseline_db_ms": BASELINE["ILIKE_search"], "db_improvement_pct": round((BASELINE["ILIKE_search"] - ea["db_exec_ms"]) / BASELINE["ILIKE_search"] * 100, 1)}
        report["queries"]["ILIKE_search_optimized"] = opt
        print(f"  DB: {BASELINE['ILIKE_search']}ms -> {ea['db_exec_ms']}ms")
        print(f"  Round-trip avg: {rt['avg_ms']}ms (rows={rt['rows']})")
    except Exception as e:
        report["queries"]["ILIKE_search_optimized"] = {"error": str(e)}
        print(f"  ERROR: {e}")
    print()
    # Caching test
    mon = pm.DashboardPerfMonitor(cache_ttl=300.0)
    mon.page_load_start()
    for label, sql, params, ck in QUERIES.values():
        if ck:
            mon.run_query(label, sql, params, cache_key=ck)
        else:
            mon.run_query(label, sql, params)
    first = mon.snapshot()
    for label, sql, params, ck in QUERIES.values():
        if ck:
            mon.run_query(label, sql, params, cache_key=ck)
    second = mon.snapshot()
    report["caching"] = {
        "first_load": {"query_count": first.query_count, "db_time_ms": round(first.db_time_ms, 2), "roundtrip_ms": round(first.roundtrip_ms, 2), "cache_hits": first.cache_hits, "cache_misses": first.cache_misses, "cache_hit_rate": first.cache_hit_rate},
        "second_load": {"query_count": second.query_count - first.query_count, "db_time_ms": round(second.db_time_ms - first.db_time_ms, 2), "roundtrip_ms": round(second.roundtrip_ms - first.roundtrip_ms, 2), "cache_hits": second.cache_hits - first.cache_hits, "cache_misses": second.cache_misses - first.cache_misses, "cache_hit_rate": second.cache_hit_rate},
        "cached_query_types": [label for label, sql, params, ck in QUERIES.values() if ck],
    }
    print("=== Caching Test ===")
    print(f"  First: {first.query_count} queries, DB={round(first.db_time_ms,2)}ms, hits={first.cache_hits}, misses={first.cache_misses}")
    print(f"  Second: {second.query_count - first.query_count} queries, DB={round(second.db_time_ms - first.db_time_ms,2)}ms, hits={second.cache_hits - first.cache_hits}")
    print()
    # Summary
    slow_db = [n for n, r in report["queries"].items() if "db_exec_ms" in r and r["db_exec_ms"] > 100]
    slow_rt = [n for n, r in report["queries"].items() if "roundtrip_benchmark" in r and r["roundtrip_benchmark"]["avg_ms"] > 100]
    improvements = [r["db_improvement_pct"] for r in report["queries"].values() if "db_improvement_pct" in r]
    avg_imp = round(sum(improvements) / len(improvements), 1) if improvements else 0
    report["summary"] = {
        "total_queries_tested": len(QUERIES) + 1,
        "slow_db_queries_after": slow_db,
        "slow_roundtrip_queries": slow_rt,
        "avg_db_improvement_pct": avg_imp,
        "cache_first_load_db_ms": round(first.db_time_ms, 2),
        "cache_second_load_db_ms": round(second.db_time_ms - first.db_time_ms, 2),
        "cache_elimination_ms": round(first.db_time_ms - (second.db_time_ms - first.db_time_ms), 2),
    }
    print("=== Summary ===")
    print(f"  Slow DB queries after optimization: {slow_db}")
    print(f"  Slow round-trip queries: {slow_rt}")
    print(f"  Avg DB improvement: {avg_imp}%")
    print()
    # Write full benchmark
    bench_path = DATA_DIR / "p44_benchmark_full.json"
    bench_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"Full benchmark saved to {bench_path}")
    return report


if __name__ == "__main__":
    main()
