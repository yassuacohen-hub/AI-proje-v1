"""Dashboard performance monitoring and query optimization utilities.

Provides:
  - QueryProfiler: tracks DB execution time, query count, per-query timing
  - CacheStats: tracks cache hit/miss ratios
  - DashboardPerfMonitor: combined monitor with profiled query executor

Usage:
    from company_master.dashboard.perf_monitor import DashboardPerfMonitor

    mon = DashboardPerfMonitor()
    result = mon.run_query("KPI", sql, params)
    metrics = mon.snapshot()
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator

from sqlalchemy import text
from company_master.db.connection import get_engine


@dataclass
class QueryRecord:
    name: str
    db_ms: float
    roundtrip_ms: float
    rows: int = 0
    cache_hit: bool = False


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0

    @property
    def total(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        return round(self.hits / self.total, 4) if self.total > 0 else 0.0


@dataclass
class PerfSnapshot:
    query_count: int = 0
    db_time_ms: float = 0.0
    roundtrip_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    queries: list = field(default_factory=list)
    page_load_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "query_count": self.query_count,
            "db_time_ms": round(self.db_time_ms, 2),
            "roundtrip_ms": round(self.roundtrip_ms, 2),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hit_rate,
            "page_load_ms": round(self.page_load_ms, 2),
            "queries": self.queries,
        }


class DashboardPerfMonitor:
    """Tracks performance metrics for dashboard queries with caching support."""

    def __init__(self, cache_ttl: float = 300.0) -> None:
        self._queries: list = []
        self._cache: dict = {}
        self._cache_ttl = cache_ttl
        self._cache_stats = CacheStats()
        self._page_start: float | None = None

    def page_load_start(self) -> None:
        self._page_start = time.perf_counter()

    @contextmanager
    def measure_page(self) -> Iterator["DashboardPerfMonitor"]:
        self.page_load_start()
        try:
            yield self
        finally:
            pass

    def _cache_get(self, key: str):
        entry = self._cache.get(key)
        if entry and time.time() - entry[0] < self._cache_ttl:
            self._cache_stats.hits += 1
            return entry[1]
        self._cache_stats.misses += 1
        if entry:
            self._cache.pop(key, None)
        return None

    def _cache_set(self, key: str, value) -> None:
        self._cache[key] = (time.time(), value)

    def _cache_clear(self) -> None:
        self._cache.clear()

    @property
    def cache_stats(self) -> CacheStats:
        return self._cache_stats

    def run_query(self, name: str, sql: str, params: dict | None = None,
                  *, cache_key: str | None = None, engine=None) -> Any:
        """Execute a query with profiling. Returns mapped rows or scalar.

        If cache_key is provided, attempts cache first (hit/miss tracked).
        """
        if cache_key is not None:
            cached = self._cache_get(cache_key)
            if cached is not None:
                self._queries.append(QueryRecord(
                    name=name, db_ms=0.0, roundtrip_ms=0.0, rows=0, cache_hit=True
                ))
                return cached

        eng = engine or get_engine()
        t0 = time.perf_counter()
        with eng.connect() as conn:
            result = conn.execute(text(sql), params or {}).mappings()
            rows = result.all() if hasattr(result, "all") else result
            db_ms = (time.perf_counter() - t0) * 1000
            roundtrip_ms = db_ms

        data = [dict(r) for r in rows] if rows else []
        self._queries.append(QueryRecord(
            name=name, db_ms=db_ms, roundtrip_ms=roundtrip_ms,
            rows=len(data), cache_hit=False
        ))

        if cache_key is not None:
            self._cache_set(cache_key, data)

        return data

    def run_scalar(self, name: str, sql: str, params: dict | None = None) -> Any:
        """Execute a query and return a single scalar value with profiling."""
        t0 = time.perf_counter()
        eng = get_engine()
        with eng.connect() as conn:
            val = conn.execute(text(sql), params or {}).scalar()
        db_ms = (time.perf_counter() - t0) * 1000
        self._queries.append(QueryRecord(
            name=name, db_ms=db_ms, roundtrip_ms=db_ms, rows=1, cache_hit=False
        ))
        return val

    def snapshot(self) -> PerfSnapshot:
        snap = PerfSnapshot()
        snap.query_count = len(self._queries)
        snap.db_time_ms = sum(q.db_ms for q in self._queries)
        snap.roundtrip_ms = sum(q.roundtrip_ms for q in self._queries)
        snap.cache_hits = self._cache_stats.hits
        snap.cache_misses = self._cache_stats.misses
        snap.cache_hit_rate = self._cache_stats.hit_rate
        snap.queries = [
            {
                "name": q.name,
                "db_ms": round(q.db_ms, 2),
                "roundtrip_ms": round(q.roundtrip_ms, 2),
                "rows": q.rows,
                "cache_hit": q.cache_hit,
            }
            for q in self._queries
        ]
        if self._page_start is not None:
            snap.page_load_ms = (time.perf_counter() - self._page_start) * 1000
        return snap

    def reset(self) -> None:
        self._queries.clear()
        self._cache.clear()
        self._cache_stats = CacheStats()
        self._page_start = None


# ---- Dashboard-optimized query templates ----

KPI_QUERY = """
    SELECT COUNT(*) AS total,
      SUM(CASE WHEN c.tax_number IS NOT NULL AND c.tax_number != '' THEN 1 ELSE 0 END) AS tax,
      SUM(CASE WHEN c.vergi_no IS NOT NULL AND c.vergi_no != '' THEN 1 ELSE 0 END) AS vergi,
      SUM(CASE WHEN COALESCE(c.tax_number, c.vergi_no) IS NOT NULL AND COALESCE(c.tax_number, c.vergi_no) != '' THEN 1 ELSE 0 END) AS vkn_either,
      SUM(CASE WHEN c.website_domain IS NOT NULL AND c.website_domain != '' THEN 1 ELSE 0 END) AS web,
      SUM(CASE WHEN c.osb_parsel IS NOT NULL AND c.osb_parsel != '' THEN 1 ELSE 0 END) AS parsel,
      SUM(CASE WHEN c.adres IS NOT NULL AND c.adres != '' THEN 1 ELSE 0 END) AS adres,
      SUM(CASE WHEN c.primary_phone IS NOT NULL AND c.primary_phone != '' THEN 1 ELSE 0 END) AS tel,
      SUM(CASE WHEN c.primary_email IS NOT NULL AND c.primary_email != '' THEN 1 ELSE 0 END) AS email,
      SUM(CASE WHEN c.nace_code IS NOT NULL AND c.nace_code != '' THEN 1 ELSE 0 END) AS nace,
      AVG(c.data_quality_score) AS avg_score
    FROM companies c
    WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
"""

SOURCES_QUERY = """
    SELECT s.source_name, s.source_type,
      COUNT(sr.source_record_id) AS record_count,
      MAX(sr.collected_at) AS last_scrape
    FROM sources s
    LEFT JOIN source_records sr ON sr.source_id = s.source_id
    GROUP BY s.source_id, s.source_name, s.source_type
    ORDER BY record_count DESC
"""

COMPANIES_LIST_QUERY = """
    SELECT c.legal_name, c.trade_name, c.website_domain, c.primary_phone, c.primary_email,
           c.tax_number, c.vergi_no, c.nace_code, c.data_quality_score
    FROM companies c
    WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
      AND c.data_quality_score >= :min_score
      AND c.data_quality_score <= :max_score
    ORDER BY c.data_quality_score DESC
    LIMIT :limit
"""

ILIKE_SEARCH_QUERY = """
    SELECT c.legal_name, c.trade_name, c.website_domain, c.primary_phone, c.primary_email,
           c.tax_number, c.vergi_no, c.nace_code, c.data_quality_score
    FROM companies c
    WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
      AND (c.legal_name ILIKE :search
           OR c.trade_name ILIKE :search
           OR c.primary_phone ILIKE :search
           OR c.primary_email ILIKE :search
           OR c.tax_number ILIKE :search
           OR c.vergi_no ILIKE :search)
    ORDER BY c.data_quality_score DESC
    LIMIT 50
"""


ILIKE_SEARCH_OPTIMIZED_QUERY = """
    SELECT c.legal_name, c.trade_name, c.website_domain, c.primary_phone, c.primary_email,
           c.tax_number, c.vergi_no, c.nace_code, c.data_quality_score
    FROM companies c
    WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
      AND c.search_text ILIKE :search
    ORDER BY c.data_quality_score DESC
    LIMIT 50
"""
SOURCE_FILTER_QUERY = """
    SELECT c.legal_name, c.trade_name, c.website_domain, c.primary_phone, c.primary_email,
           c.tax_number, c.vergi_no, c.nace_code, c.data_quality_score
    FROM companies c
    WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
      AND c.source_record_id IN (
        SELECT sr.source_record_id
        FROM source_records sr
        JOIN sources s ON sr.source_id = s.source_id
        WHERE s.source_name = :source_name
      )
    ORDER BY c.data_quality_score DESC
    LIMIT 50
"""

ASO_COUNT_QUERY = """
    SELECT COUNT(*) FROM source_records sr
    WHERE sr.source_id = (SELECT source_id FROM sources WHERE source_name = 'aso.org.tr' LIMIT 1)
"""

QUALITY_TREND_QUERY = """
    SELECT CASE
        WHEN data_quality_score >= 80 THEN '80-100'
        WHEN data_quality_score >= 60 THEN '60-79'
        WHEN data_quality_score >= 40 THEN '40-59'
        WHEN data_quality_score >= 20 THEN '20-39'
        ELSE '0-19'
    END AS bucket, COUNT(*) AS cnt
    FROM companies
    WHERE is_ankara=TRUE AND is_osb_member=TRUE
    GROUP BY 1
    ORDER BY 1 DESC
"""

NACE_DISTRIBUTION_QUERY = """
    SELECT nace_code, COUNT(*) AS cnt
    FROM companies
    WHERE is_ankara=TRUE AND is_osb_member=TRUE
      AND nace_code IS NOT NULL AND nace_code != ''
    GROUP BY nace_code
    ORDER BY cnt DESC
    LIMIT 20
"""

