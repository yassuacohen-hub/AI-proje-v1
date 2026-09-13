# -*- coding: utf-8 -*-
"""API Rate Limiter — merkezi rate limiting modulu.

Tum endpoint'ler bu modul uzerinden gerceklesir:
- Tier bazli limit (public, user, analyst, admin)
- Per-user limit esnekligi
- Burst mode (gecici limit aşı)
- Whitelist destegi (zone atlaması)
- Per-IP sliding window
- Per-endpoint ek limit
- Thread-safe (Lock ile korumali)

Kullanim:
    from src.company_master.api.rate_limiter import RateLimiter

    limiter = RateLimiter()
    allowed, retry_after = limiter.check("192.168.1.1", tier="public")
    if allowed:
        limiter.consume("192.168.1.1", tier="public")
"""
from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_TIER_LIMITS: dict[str, int] = {
    "public": 30,
    "user": 60,
    "analyst": 120,
    "admin": 300,
}
DEFAULT_WINDOW_SECONDS = 60
DEFAULT_RATE_LIMIT_MAX = 1000
DEFAULT_BURST_MULTIPLIER = 2.0
DEFAULT_BURST_WINDOW_SECONDS = 10


@dataclass
class RateLimitResult:
    allowed: bool
    retry_after: float = 0.0
    current_count: int = 0
    limit: int = 0
    window_seconds: int = 0
    burst: bool = False
    whitelisted: bool = False


class RateLimiter:
    """Thread-safe, tier-based API rate limiter with burst and whitelist."""

    def __init__(
        self,
        tier_limits: dict[str, int] | None = None,
        window_seconds: int = DEFAULT_WINDOW_SECONDS,
        rate_limit_max: int = DEFAULT_RATE_LIMIT_MAX,
        burst_multiplier: float = DEFAULT_BURST_MULTIPLIER,
        burst_window_seconds: int = DEFAULT_BURST_WINDOW_SECONDS,
        whitelist_ips: set[str] | None = None,
        whitelist_users: set[str] | None = None,
    ) -> None:
        self._tier_limits = tier_limits or DEFAULT_TIER_LIMITS.copy()
        self._window = window_seconds
        self._max = rate_limit_max
        self._burst_multiplier = burst_multiplier
        self._burst_window = burst_window_seconds
        self._whitelist_ips = whitelist_ips or set()
        self._whitelist_users = whitelist_users or set()
        self._lock = Lock()
        # ip -> {endpoint -> [timestamps]}
        self._buckets: dict[str, dict[str, list[float]]] = defaultdict(
            lambda: defaultdict(list)
        )
        # global ip -> [timestamps]
        self._global: dict[str, list[float]] = defaultdict(list)
        # user_id -> [timestamps]
        self._user_buckets: dict[str, list[float]] = defaultdict(list)
        # ip -> burst timestamps
        self._burst: dict[str, list[float]] = defaultdict(list)

    def is_whitelisted(self, ip: str, user_id: str = "") -> bool:
        """IP veya user whitelist kontrolu."""
        if ip in self._whitelist_ips:
            return True
        if user_id and user_id in self._whitelist_users:
            return True
        return False

    def check(
        self,
        ip: str,
        tier: str = "public",
        endpoint: str = "",
        user_id: str = "",
    ) -> RateLimitResult:
        """Check if request is allowed. Does NOT consume."""
        now = time.time()
        with self._lock:
            if self.is_whitelisted(ip, user_id):
                return RateLimitResult(
                    allowed=True,
                    retry_after=0.0,
                    current_count=0,
                    limit=0,
                    window_seconds=0,
                    whitelisted=True,
                )

            global_count = self._prune(self._global.get(ip, []), now)
            endpoint_count = (
                self._prune(self._buckets[ip][endpoint], now)
                if endpoint
                else []
            )
            user_count = self._prune(self._user_buckets.get(user_id, []), now)

            limit = self._tier_limits.get(tier, self._max)
            burst_limit = int(limit * self._burst_multiplier)
            endpoint_limit = limit

            is_burst = False
            if len(global_count) >= limit and len(global_count) < burst_limit:
                burst_ts = self._prune(self._burst.get(ip, []), now)
                if len(burst_ts) < 5:
                    is_burst = True
                    self._burst.setdefault(ip, [])
                    self._burst[ip].append(now)
                    self._burst[ip] = self._prune(self._burst[ip], now)

            if len(global_count) >= burst_limit and is_burst is False:
                oldest = global_count[0] if global_count else now
                return RateLimitResult(
                    allowed=False,
                    retry_after=max(0.0, self._window - (now - oldest)),
                    current_count=len(global_count),
                    limit=limit,
                    window_seconds=self._window,
                )

            if len(endpoint_count) >= endpoint_limit:
                oldest = endpoint_count[0] if endpoint_count else now
                return RateLimitResult(
                    allowed=False,
                    retry_after=max(0.0, self._window - (now - oldest)),
                    current_count=len(endpoint_count),
                    limit=endpoint_limit,
                    window_seconds=self._window,
                )

            return RateLimitResult(
                allowed=True,
                retry_after=0.0,
                current_count=len(global_count),
                limit=limit,
                window_seconds=self._window,
                burst=is_burst,
            )

    def consume(
        self,
        ip: str,
        tier: str = "public",
        endpoint: str = "",
        user_id: str = "",
    ) -> RateLimitResult:
        """Consume one request slot. Returns result with updated counts."""
        now = time.time()
        with self._lock:
            if self.is_whitelisted(ip, user_id):
                return RateLimitResult(
                    allowed=True, retry_after=0.0, whitelisted=True
                )

            self._global.setdefault(ip, [])
            self._global[ip].append(now)
            self._global[ip] = self._prune(self._global[ip], now)

            if endpoint:
                self._buckets[ip][endpoint].append(now)
                self._buckets[ip][endpoint] = self._prune(
                    self._buckets[ip][endpoint], now
                )

            if user_id:
                self._user_buckets.setdefault(user_id, [])
                self._user_buckets[user_id].append(now)
                self._user_buckets[user_id] = self._prune(
                    self._user_buckets[user_id], now
                )

            limit = self._tier_limits.get(tier, self._max)
            return RateLimitResult(
                allowed=True,
                retry_after=0.0,
                current_count=len(self._global[ip]),
                limit=limit,
                window_seconds=self._window,
            )

    def reset(self, ip: str, endpoint: str = "") -> None:
        with self._lock:
            if endpoint:
                self._buckets[ip][endpoint].clear()
            else:
                self._global[ip].clear()

    def status(self, ip: str = "") -> dict[str, Any]:
        with self._lock:
            now = time.time()
            if ip:
                ips = {ip}
            else:
                ips = list(self._global.keys())

            result: dict[str, Any] = {
                "total_ips": len(ips),
                "window_seconds": self._window,
                "tier_limits": self._tier_limits,
                "burst_multiplier": self._burst_multiplier,
                "burst_window_seconds": self._burst_window,
                "whitelist_ips": list(self._whitelist_ips),
                "whitelist_users": list(self._whitelist_users),
                "details": {},
            }
            for client_ip in ips:
                global_ts = self._prune(self._global.get(client_ip, []), now)
                endpoints: dict[str, int] = {}
                for ep, ts_list in self._buckets.get(client_ip, {}).items():
                    endpoints[ep] = len(self._prune(ts_list, now))
                user_count = len(self._prune(
                    self._user_buckets.get(client_ip, []), now
                ))
                result["details"][client_ip] = {
                    "global_count": len(global_ts),
                    "limit": self._tier_limits.get("public", self._max),
                    "endpoints": endpoints,
                    "user_count": user_count,
                    "whitelisted": client_ip in self._whitelist_ips,
                }
            return result

    def add_whitelist_ip(self, ip: str) -> None:
        with self._lock:
            self._whitelist_ips.add(ip)

    def remove_whitelist_ip(self, ip: str) -> None:
        with self._lock:
            self._whitelist_ips.discard(ip)

    def add_whitelist_user(self, user_id: str) -> None:
        with self._lock:
            self._whitelist_users.add(user_id)

    def remove_whitelist_user(self, user_id: str) -> None:
        with self._lock:
            self._whitelist_users.discard(user_id)

    @staticmethod
    def _prune(timestamps: list[float], now: float) -> list[float]:
        cutoff = now - DEFAULT_WINDOW_SECONDS
        return [t for t in timestamps if t >= cutoff]

    def get_retry_after(
        self, ip: str, tier: str = "public", endpoint: str = ""
    ) -> float:
        result = self.check(ip, tier=tier, endpoint=endpoint)
        return result.retry_after


_global_limiter: RateLimiter | None = None
_limiter_lock = Lock()


def get_rate_limiter() -> RateLimiter:
    """Global rate limiter instance (singleton)."""
    global _global_limiter
    if _global_limiter is None:
        with _limiter_lock:
            if _global_limiter is None:
                _global_limiter = RateLimiter()
    return _global_limiter


def check_rate_limit(ip: str, tier: str = "public") -> RateLimitResult:
    """Module-level shortcut: check rate limit for IP."""
    return get_rate_limiter().check(ip, tier=tier)


def consume_rate_limit(ip: str, tier: str = "public") -> RateLimitResult:
    """Module-level shortcut: consume rate limit for IP."""
    return get_rate_limiter().consume(ip, tier=tier)
