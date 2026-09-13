# -*- coding: utf-8 -*-
"""P7-36: Redis cache layer.

Redis cache layer with TTL, namespace, fallback to in-memory.

Kullanim:
    from src.company_master.cache.redis_cache import RedisCache

    cache = RedisCache(host="localhost", port=6379, db=0)
    cache.set("key", {"data": "value"}, ttl=300)
    data = cache.get("key")
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

import redis

logger = logging.getLogger(__name__)

DEFAULT_TTL = 300
DEFAULT_PORT = 6379
DEFAULT_DB = 0


class _InMemoryFallback:
    """Redis unavailable icin in-memory fallback."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry and time.time() < entry[0]:
            return entry[1]
        self._store.pop(key, None)
        return None

    def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
        self._store[key] = (time.time() + ttl, value)
        return True

    def delete(self, key: str) -> int:
        return self._store.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        return self._store.get(key) is not None

    def flush(self) -> int:
        count = len(self._store)
        self._store.clear()
        return count


class RedisCache:
    """Redis cache layer with in-memory fallback."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = DEFAULT_PORT,
        db: int = DEFAULT_DB,
        password: str | None = None,
        decode_responses: bool = True,
        fallback: bool = True,
    ) -> None:
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._decode_responses = decode_responses
        self._fallback_enabled = fallback
        self._client: redis.Redis | None = None
        self._fallback = _InMemoryFallback() if fallback else None
        self._connected = False
        self._connect()

    def _connect(self) -> None:
        try:
            self._client = redis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password,
                decode_responses=self._decode_responses,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            self._client.ping()
            self._connected = True
            logger.info("Redis baglandi: %s:%s/db=%s", self._host, self._port, self._db)
        except Exception as e:
            self._connected = False
            logger.warning(
                "Redis baglanamadi (%s:%s), in-memory fallback: %s",
                self._host,
                self._port,
                e,
            )

    @property
    def connected(self) -> bool:
        return self._connected

    def _get_client(self) -> redis.Redis | _InMemoryFallback:
        if self._connected and self._client:
            return self._client
        if self._fallback is not None:
            return self._fallback
        raise RuntimeError("Redis cache baglanilamadi ve fallback yok")

    def get(self, key: str) -> Any | None:
        client = self._get_client()
        try:
            if isinstance(client, redis.Redis):
                raw = client.get(key)
                if raw is None:
                    return None
                return json.loads(raw)
            return client.get(key)
        except Exception as e:
            logger.warning("Cache get hatasi: %s", e)
            if self._fallback:
                return self._fallback.get(key)
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int = DEFAULT_TTL,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        client = self._get_client()
        try:
            if isinstance(client, redis.Redis):
                serialized = json.dumps(value, ensure_ascii=False)
                if nx:
                    return bool(client.set(key, serialized, ex=ttl, nx=True))
                if xx:
                    return bool(client.set(key, serialized, ex=ttl, xx=True))
                return bool(client.set(key, serialized, ex=ttl))
            return client.set(key, value, ttl)
        except Exception as e:
            logger.warning("Cache set hatasi: %s", e)
            if self._fallback:
                if nx and client.exists(key):
                    return False
                return client.set(key, value, ttl)
            return False

    def delete(self, *keys: str) -> int:
        client = self._get_client()
        try:
            if isinstance(client, redis.Redis):
                return client.delete(*keys)
            count = 0
            for key in keys:
                if client.delete(key):
                    count += 1
            return count
        except Exception as e:
            logger.warning("Cache delete hatasi: %s", e)
            return 0

    def exists(self, key: str) -> bool:
        client = self._get_client()
        try:
            if isinstance(client, redis.Redis):
                return bool(client.exists(key))
            return client.exists(key)
        except Exception:
            return False

    def expire(self, key: str, ttl: int) -> bool:
        client = self._get_client()
        try:
            if isinstance(client, redis.Redis):
                return bool(client.expire(key, ttl))
            return False
        except Exception:
            return False

    def flush(self) -> int:
        client = self._get_client()
        try:
            if isinstance(client, redis.Redis):
                return client.flushdb()
            return client.flush()
        except Exception:
            return 0

    def keys(self, pattern: str = "*") -> list[str]:
        client = self._get_client()
        try:
            if isinstance(client, redis.Redis):
                return [k.decode() if isinstance(k, bytes) else k for k in client.keys(pattern)]
            return []
        except Exception:
            return []

    def ping(self) -> bool:
        if self._connected and self._client:
            try:
                return bool(self._client.ping())
            except Exception:
                return False
        return False

    def get_ttl(self, key: str) -> int | None:
        client = self._get_client()
        try:
            if isinstance(client, redis.Redis):
                ttl = client.ttl(key)
                return ttl if ttl >= 0 else None
            return None
        except Exception:
            return None


_cache_instance: RedisCache | None = None


def get_cache() -> RedisCache:
    """Global cache instance (singleton)."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance
