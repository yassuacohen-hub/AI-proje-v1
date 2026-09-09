#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dashboard query performance benchmark."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from company_master.db.connection import get_engine
from sqlalchemy import text

QUERIES = []

def bench(name, sql, params=None):
    start = time.perf_counter()
    try:
        with get_engine().connect() as conn:
            r = conn.execute(text(sql), params or {}).mappings().all()
            ms = (time.perf_counter() - start) * 1000
            rows = len(r)
            print(f"{name}: {ms:.1f} ms | rows={rows}")
            if ms > 100:
                QUERIES.append({"name": name, "ms": round(ms, 1), "rows": rows, "status": "SLOW"})
            else:
                QUERIES.append({"name": name, "ms": round(ms, 1), "rows": rows, "status": "OK"})
            return r
    except Exception as e:
        ms = (time.perf_counter() - start) * 1000
        print(f"{name}: FAILED ({ms:.1f} ms) - {e}")
        QUERIES.append({"name": name, "ms": round(ms, 1), "rows": 0, "status": "FAILED", "error": str(e)})
        return []


if __name__ == "__main__":
    print("=== Dashboard Query Benchmark ===\n")

    bench("KPI", """
        SELECT COUNT(*) as total,
            SUM(CASE WHEN tax_number IS NOT NULL AND tax_number != '' THEN 1 ELSE 0 END) as tax,
            SUM(CASE WHEN vergi_no IS NOT NULL AND vergi_no != '' THEN 1 ELSE 0 END) as vergi,
            SUM(CASE WHEN COALESCE(tax_number, vergi_no) IS NOT NULL AND COALESCE(tax_number, vergi_no) != '' THEN 1 ELSE 0 END) as vkn_either,
            SUM(CASE WHEN website_domain IS NOT NULL AND website_domain != '' THEN 1 ELSE 0 END) as web,
            SUM(CASE WHEN osb_parsel IS NOT NULL AND osb_parsel != '' THEN 1 ELSE 0 END) as parsel,
            SUM(CASE WHEN adres IS NOT NULL AND adres != '' THEN 1 ELSE 0 END) as adres,
            SUM(CASE WHEN primary_phone IS NOT NULL AND primary_phone != '' THEN 1 ELSE 0 END) as tel,
            SUM(CASE WHEN primary_email IS NOT NULL AND primary_email != '' THEN 1 ELSE 0 END) as email,
            SUM(CASE WHEN nace_code IS NOT NULL AND nace_code != '' THEN 1 ELSE 0 END) as nace,
            AVG(data_quality_score) as avg_score
        FROM companies
        WHERE is_ankara=TRUE AND is_osb_member=TRUE
    """)

    bench("Sources", """
        SELECT s.source_name, COUNT(sr.source_record_id) as cnt
        FROM sources s
        LEFT JOIN source_records sr ON sr.source_id = s.source_id
        GROUP BY s.source_id, s.source_name
        ORDER BY cnt DESC
    """)

    bench("ASO count", """
        SELECT COUNT(*) FROM source_records sr
        WHERE sr.source_id = (SELECT source_id FROM sources WHERE source_name = 'aso.org.tr' LIMIT 1)
    """)

    bench("Companies list", """
        SELECT legal_name, trade_name, website_domain, primary_phone, primary_email,
               tax_number, vergi_no, nace_code, data_quality_score
        FROM companies
        WHERE is_ankara=TRUE AND is_osb_member=TRUE
        ORDER BY data_quality_score DESC
        LIMIT 200
    """)

    bench("Quality trend", """
        SELECT CASE
            WHEN data_quality_score >= 80 THEN '80-100'
            WHEN data_quality_score >= 60 THEN '60-79'
            WHEN data_quality_score >= 40 THEN '40-59'
            WHEN data_quality_score >= 20 THEN '20-39'
            ELSE '0-19'
        END as bucket, COUNT(*) as cnt
        FROM companies
        WHERE is_ankara=TRUE AND is_osb_member=TRUE
        GROUP BY 1
        ORDER BY 1 DESC
    """)

    bench("NACE distribution", """
        SELECT nace_code, COUNT(*) as cnt
        FROM companies
        WHERE is_ankara=TRUE AND is_osb_member=TRUE AND nace_code IS NOT NULL AND nace_code != ''
        GROUP BY nace_code
        ORDER BY cnt DESC
        LIMIT 20
    """)

    bench("ILIKE search", """
        SELECT legal_name, trade_name, website_domain, primary_phone, primary_email,
               tax_number, vergi_no, data_quality_score
        FROM companies
        WHERE is_ankara=TRUE AND is_osb_member=TRUE
        AND (legal_name ILIKE :search OR tax_number ILIKE :search OR vergi_no ILIKE :search)
        ORDER BY data_quality_score DESC
        LIMIT 50
    """, params={"search": "%OSTIM%"})

    bench("Source EXISTS filter", """
        SELECT legal_name, trade_name, website_domain, primary_phone, primary_email,
               tax_number, vergi_no, nace_code, data_quality_score
        FROM companies c
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND EXISTS (
            SELECT 1 FROM source_records sr
            JOIN sources s ON sr.source_id = s.source_id
            WHERE sr.source_record_id = c.source_record_id
            AND s.source_name = 'ostim.org.tr'
        )
        ORDER BY c.data_quality_score DESC
        LIMIT 50
    """)

    bench("Metrics KPI (web_app)", """
        SELECT COUNT(*) as total,
            AVG(data_quality_score) as avg_score,
            SUM(CASE WHEN tax_number IS NOT NULL AND tax_number != '' THEN 1 ELSE 0 END) as with_tax,
            SUM(CASE WHEN website_domain IS NOT NULL AND website_domain != '' THEN 1 ELSE 0 END) as with_web,
            SUM(CASE WHEN nace_code IS NOT NULL AND nace_code != '' THEN 1 ELSE 0 END) as with_nace,
            SUM(CASE WHEN primary_phone IS NOT NULL AND primary_phone != '' THEN 1 ELSE 0 END) as with_phone,
            SUM(CASE WHEN primary_email IS NOT NULL AND primary_email != '' THEN 1 ELSE 0 END) as with_email,
            SUM(CASE WHEN osb_parsel IS NOT NULL AND osb_parsel != '' THEN 1 ELSE 0 END) as with_parsel,
            SUM(CASE WHEN adres IS NOT NULL AND adres != '' THEN 1 ELSE 0 END) as with_adres
        FROM companies
        WHERE is_ankara=TRUE
    """)

    print("\n=== Summary ===")
    slow = [q for q in QUERIES if q["status"] == "SLOW"]
    failed = [q for q in QUERIES if q["status"] == "FAILED"]
    print(f"Total queries: {len(QUERIES)}")
    print(f"Slow (>100ms): {len(slow)}")
    print(f"Failed: {len(failed)}")
    if slow:
        print("\nSlow queries:")
        for q in slow:
            print(f"  - {q['name']}: {q['ms']} ms")

    import json
    out_path = Path(__file__).resolve().parents[1] / "data" / "orchestrator" / "p44_query_benchmark.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_queries": len(QUERIES),
        "slow_count": len(slow),
        "failed_count": len(failed),
        "queries": QUERIES
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved to {out_path}")
