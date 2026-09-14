# -*- coding: utf-8 -*-
"""Admin API caching layer (BE-01).

Redis tabanli admin panel endpoint cache'i.
Kullanim:
    from src.company_master.admin.caching import admin_cache
    
    @admin_cache(ttl=60)
    def get_kpi_data():
        ...
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.cache.redis_cache import RedisCache

_cache: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """Redis cache instansi (lazy init)."""
    global _cache
    if _cache is None:
        try:
            _cache = RedisCache()
        except Exception:
            from src.company_master.cache.redis_cache import _InMemoryFallback
            _cache = _InMemoryFallback()  # type: ignore
    return _cache


def _make_key(prefix: str, *args, **kwargs) -> str:
    """Cache key olustur."""
    raw = json.dumps({"a": args, "k": kwargs}, sort_keys=True)
    h = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return f"admin:{prefix}:{h}"


def admin_cache(ttl: int = 60):
    """Admin endpoint cache decorator.
    
    Redis capali, in-memory fallback sunar.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            key = _make_key(func.__name__, *args, **kwargs)
            cache = get_cache()
            
            cached = cache.get(key)
            if cached is not None:
                return cached
            
            result = func(*args, **kwargs)
            cache.set(key, result, ttl=ttl)
            return result
        return wrapper
    return decorator


def admin_cache_invalidate(prefix: str) -> int:
    """Tum bu prefix cache'ini sil.
    
    Veri degistiginde kullanilir.
    """
    cache = get_cache()
    # Pattern matching for Redis keys (fallback: clear all admin keys)
    try:
        keys = cache._redis.keys(f"admin:{prefix}:*") if hasattr(cache, '_redis') else []
        if keys:
            return cache._redis.delete(*keys)  # type: ignore
    except Exception:
        pass
    return 0


def admin_cache_stats() -> dict[str, Any]:
    """Cache istatistiklerini getir."""
    cache = get_cache()
    return {
        "type": type(cache).__name__,
        "hits": getattr(cache, "_hits", 0),
        "misses": getattr(cache, "_misses", 0),
    }