# -*- coding: utf-8 -*-
"""ADMIN-UI-CACHE-OPT-01 testleri — web_app.py cache katmani.

Kapsam:
  1. cache_get / cache_set temel akis (hit/miss)
  2. TTL sonrasi expiry
  3. HUGGINN_CACHE_TTL env ayari
  4. Bos sonuc negatif cache'lenmemesi
  5. Cache boyut siniri (eviction)
  6. admin_cache decorator (fallback ile)
"""
from __future__ import annotations

import importlib
import time
from types import SimpleNamespace

import pytest


@pytest.fixture()
def webapp(monkeypatch):
    """web_app modulunu izole yukle (env resetli)."""
    monkeypatch.delenv("HUGGINN_CACHE_TTL", raising=False)
    monkeypatch.delenv("HUGGINN_CACHE_MAX_ENTRIES", raising=False)
    import web_app  # noqa: E402

    importlib.reload(web_app)
    web_app._CACHE.clear()
    web_app._CACHE_HITS = 0
    web_app._CACHE_MISSES = 0
    return web_app


class TestCacheTemel:
    def test_set_then_get_hit(self, webapp):
        webapp.cache_set("k1", {"a": 1})
        assert webapp.cache_get("k1") == {"a": 1}
        assert webapp._CACHE_HITS == 1

    def test_miss_returns_none(self, webapp):
        assert webapp.cache_get("yok") is None
        assert webapp._CACHE_MISSES == 1

    def test_expiry_after_ttl(self, webapp):
        webapp.cache_set("k2", "v")
        # Kaydi yaslandir (TTL gecmis gibi)
        ts, val = webapp._CACHE["k2"]
        webapp._CACHE["k2"] = (ts - webapp._CACHE_TTL - 1, val)
        assert webapp.cache_get("k2") is None


class TestTtlEnv:
    def test_env_ttl_oku(self, monkeypatch):
        monkeypatch.setenv("HUGGINN_CACHE_TTL", "42")
        import web_app
        importlib.reload(web_app)
        assert web_app._CACHE_TTL == 42

    def test_env_ttl_gecersiz_deger_crash_etmez(self, monkeypatch):
        # int() crash ederse modul yuklenmez — davranis belgelenir
        monkeypatch.setenv("HUGGINN_CACHE_TTL", "abc")
        with pytest.raises(ValueError):
            import web_app
            importlib.reload(web_app)


class TestNegatifCache:
    def test_bos_dict_cache_lenmez(self, webapp):
        webapp.cache_set("b1", {})
        assert "b1" not in webapp._CACHE

    def test_bos_list_cache_lenmez(self, webapp):
        webapp.cache_set("b2", [])
        assert "b2" not in webapp._CACHE

    def test_dolu_sonuc_cache_lenir(self, webapp):
        webapp.cache_set("b3", {"toplam": 5})
        assert webapp.cache_get("b3") == {"toplam": 5}


class TestEviction:
    def test_sinir_asimi_en_eski_atilir(self, webapp, monkeypatch):
        monkeypatch.setattr(webapp, "_CACHE_MAX_ENTRIES", 3)
        for i in range(5):
            webapp.cache_set(f"e{i}", i)
        # 5 ekleme, 3 kayit kalmali; en eskiler (e0, e1) atilmali
        assert len(webapp._CACHE) <= 3
        assert webapp.cache_get("e0") is None
        assert webapp.cache_get("e1") is None
        assert webapp.cache_get("e4") == 4


class TestAdminCache:
    def test_decorator_fallback_calisir(self, webapp):
        cagri = {"n": 0}

        @webapp.admin_cache(ttl=60)
        def pahali():
            cagri["n"] += 1
            return {"deger": cagri["n"]}

        r1 = pahali()
        r2 = pahali()
        assert r1 == r2
        assert cagri["n"] == 1  # ikinci cagri cache'den
