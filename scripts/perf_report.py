# -*- coding: utf-8 -*-
"""P4-4: Performans profili — API latency + EXPLAIN ANALYZE."""
import sys, time, json, urllib.request
sys.path.insert(0, 'src')
sys.stdout.reconfigure(encoding='utf-8')
from sqlalchemy import text
from company_master.db.connection import get_engine

BASE = "http://127.0.0.1:8000"

def timed(path, n=3):
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        try:
            urllib.request.urlopen(BASE + path, timeout=30).read()
        except Exception as e:
            return path, -1, str(e)
        times.append((time.perf_counter() - t0) * 1000)
    return path, round(sum(times) / len(times), 1), round(min(times), 1)

print("== API LATENCY (ort ms / min ms, 3 kosum) ==")
for path in ["/api/health", "/api/kpi", "/api/quality-trend", "/api/nace-distribution",
             "/api/companies?limit=50", "/api/companies?limit=200",
             "/api/companies?search=akkor", "/api/companies?nace=29&limit=50",
             "/api/companies?sources=ostim.org.tr&limit=50"]:
    p, avg, mn = timed(path)
    print(f"  {p:<48} avg={avg} min={mn}")

# /api/performance sunucu icin metrikler
try:
    with urllib.request.urlopen(BASE + "/api/performance", timeout=15) as r:
        perf = json.loads(r.read().decode('utf-8'))
    print("== /api/performance ==")
    print(f"  db_time_ms={perf.get('db_time_ms')} query_count={perf.get('query_count')} "
          f"cache_hit_rate={perf.get('cache_hit_rate')} slow={len(perf.get('slow_queries', []))}")
except Exception as e:
    print("perf endpoint:", e)

print("== EXPLAIN ANALYZE (search ILIKE) ==")
engine = get_engine()
conn = engine.connect()
plan = conn.execute(text("""
    EXPLAIN (ANALYZE, BUFFERS)
    SELECT c.legal_name, c.trade_name, c.primary_phone, c.primary_email
    FROM companies c
    WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
      AND (c.legal_name ILIKE '%akkor%' OR c.trade_name ILIKE '%akkor%')
    ORDER BY c.data_quality_score DESC
    LIMIT 50
""")).all()
for row in plan:
    line = row[0]
    if any(k in line for k in ('Execution Time', 'Index', 'Seq Scan', 'Planning Time', 'rows=', 'Sort')):
        print(f"  {line.strip()}")

