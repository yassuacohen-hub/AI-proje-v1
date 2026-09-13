# -*- coding: utf-8 -*-
"""YENI-2: API Rate Limiting Optimizasyonu testleri."""
from __future__ import annotations

import sys
from pathlib import Path
from threading import Thread

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from company_master.api.rate_limiter import (
    RateLimitResult,
    RateLimiter,
    get_rate_limiter,
    check_rate_limit,
    consume_rate_limit,
)


class TestRateLimiterBasic:
    def test_default_limits(self):
        r = RateLimiter()
        assert r._tier_limits["public"] == 30
        assert r._tier_limits["user"] == 60
        assert r._tier_limits["analyst"] == 120
        assert r._tier_limits["admin"] == 300

    def test_custom_limits(self):
        r = RateLimiter(tier_limits={"public": 5, "admin": 100})
        result = r.check("1.2.3.4", "public")
        assert result.limit == 5

    def test_check_does_not_consume(self):
        r = RateLimiter(tier_limits={"public": 2})
        result1 = r.check("1.2.3.4", "public")
        result2 = r.check("1.2.3.4", "public")
        assert result1.current_count == result2.current_count

    def test_consume_increases_count(self):
        r = RateLimiter(tier_limits={"public": 2})
        result_before = r.check("1.2.3.4", "public")
        r.consume("1.2.3.4", "public")
        result_after = r.check("1.2.3.4", "public")
        assert result_before.current_count < result_after.current_count

    def test_allows_under_limit(self):
        r = RateLimiter(tier_limits={"public": 5})
        for _ in range(4):
            r.consume("1.2.3.4", "public")
        result = r.check("1.2.3.4", "public")
        assert result.allowed is True

    def test_blocks_at_limit(self):
        r = RateLimiter(tier_limits={"public": 3}, burst_multiplier=1.0)
        for _ in range(3):
            r.consume("1.2.3.4", "public")
        result = r.check("1.2.3.4", "public")
        assert result.allowed is False
        assert result.retry_after > 0

    def test_burst_allows_temporary_exceed(self):
        r = RateLimiter(tier_limits={"public": 3}, burst_multiplier=2.0)
        for _ in range(3):
            r.consume("1.2.3.4", "public")
        result = r.check("1.2.3.4", "public")
        assert result.allowed is True
        assert result.burst is True
        for _ in range(3):
            r.consume("1.2.3.4", "public")
        result = r.check("1.2.3.4", "public")
        assert result.allowed is False

    def test_different_ips_independent(self):
        r = RateLimiter(tier_limits={"public": 2})
        r.consume("1.2.3.4", "public")
        r.consume("1.2.3.4", "public")
        result2 = r.check("5.6.7.8", "public")
        assert result2.allowed is True

    def test_endpoint_tracking(self):
        r = RateLimiter(tier_limits={"public": 3}, burst_multiplier=1.0)
        for _ in range(3):
            r.consume("1.2.3.4", "public", endpoint="/api/companies")
        result = r.check("1.2.3.4", "public", endpoint="/api/companies")
        assert result.allowed is False

    def test_empty_endpoint_shows_global_count(self):
        r = RateLimiter(tier_limits={"public": 3})
        r.consume("1.2.3.4", "public")
        result = r.check("1.2.3.4", "public", endpoint="")
        assert result.allowed is True
        assert result.current_count == 1


class TestRateLimiterReset:
    def test_reset_clears_ip(self):
        r = RateLimiter(tier_limits={"public": 1})
        r.consume("1.2.3.4", "public")
        r.reset("1.2.3.4")
        result = r.check("1.2.3.4", "public")
        assert result.allowed is True

    def test_reset_endpoint_only(self):
        r = RateLimiter(tier_limits={"public": 5})
        r.consume("1.2.3.4", "public", endpoint="/api/a")
        r.reset("1.2.3.4", "/api/a")
        result = r.check("1.2.3.4", "public", endpoint="/api/a")
        assert result.allowed is True


class TestRateLimiterStatus:
    def test_status_single_ip(self):
        r = RateLimiter()
        r.consume("1.2.3.4", "public")
        status = r.status("1.2.3.4")
        assert status["total_ips"] == 1
        assert "1.2.3.4" in status["details"]
        assert status["details"]["1.2.3.4"]["global_count"] == 1

    def test_status_all_ips(self):
        r = RateLimiter()
        r.consume("1.2.3.4", "public")
        r.consume("5.6.7.8", "user")
        status = r.status()
        assert status["total_ips"] == 2


class TestRateLimiterThreadSafe:
    def test_concurrent_access(self):
        r = RateLimiter(tier_limits={"public": 100})
        errors = []

        def worker():
            try:
                for _ in range(10):
                    r.consume("1.2.3.4", "public")
            except Exception as e:
                errors.append(e)

        threads = [Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        status = r.status("1.2.3.4")
        assert status["details"]["1.2.3.4"]["global_count"] == 50


class TestModuleLevel:
    def test_get_rate_limiter_singleton(self):
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()
        assert limiter1 is limiter2

    def test_check_rate_limit(self):
        result = check_rate_limit("1.2.3.4", "public")
        assert isinstance(result, RateLimitResult)

    def test_consume_rate_limit(self):
        result = consume_rate_limit("1.2.3.4", "public")
        assert isinstance(result, RateLimitResult)
