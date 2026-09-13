# -*- coding: utf-8 -*-
"""P7-23: VectorSearch testleri.

Gercek 9Router cagirmaz; SabitEmbedder mock ile test edilir.
"""
from __future__ import annotations

import pytest

from src.company_master.intelligence.vector_search import (
    VectorSearch,
    VectorSearchConfig,
    VectorSearchResult,
)
from src.company_master.vector.embedder import Embedder, EmbeddingResult


class SabitEmbedder(Embedder):
    """Sabit vektor donen embedder."""

    def embed(self, texts, **kw):
        vecs = []
        for t in texts:
            t = (t or "").lower()
            if "metal" in t or "celik" in t:
                vecs.append([1.0, 0.0, 0.0])
            elif "plastik" in t:
                vecs.append([0.0, 1.0, 0.0])
            else:
                vecs.append([0.0, 0.0, 1.0])
        return EmbeddingResult(embeddings=vecs, model="test", errors=[])


@pytest.fixture
def vs():
    return VectorSearch(embedder=SabitEmbedder())


@pytest.fixture
def vs_with_rows(vs):
    rows = [
        {"company_id": "c1", "legal_name": "ABC Metal", "faaliyet": "Celik"},
        {"company_id": "c2", "legal_name": "XYZ Plastik", "faaliyet": "Plastik"},
        {"company_id": "c3", "legal_name": "DEF Metal Islama", "faaliyet": "Celik sac"},
    ]
    n = vs.index_companies(rows)
    assert n == 3
    return vs


def test_config_defaults():
    cfg = VectorSearchConfig()
    assert cfg.top_k == 5
    assert cfg.where is None
    assert cfg.id_key == "company_id"


def test_config_top_k_capped(vs_with_rows):
    results = vs_with_rows.search("metal", top_k=200)
    assert len(results) == 3
    for r in results:
        assert r.score >= 0.0


def test_search_empty_query(vs):
    assert vs.search("") == []
    assert vs.search("   ") == []


def test_search_bullets(vs_with_rows):
    results = vs_with_rows.search("celik metal", top_k=2)
    assert len(results) == 2
    ids = {r.id for r in results}
    assert ids == {"c1", "c3"}
    for r in results:
        assert r.score >= 0.99


def test_search_plastik(vs_with_rows):
    results = vs_with_rows.search("plastik enjeksiyon", top_k=1)
    assert len(results) == 1
    assert results[0].id == "c2"
    assert results[0].name == "XYZ Plastik"


def test_search_result_to_dict(vs_with_rows):
    results = vs_with_rows.search("metal", top_k=1)
    assert len(results) == 1
    d = results[0].to_dict()
    assert d["id"] in {"c1", "c3"}
    assert d["score"] >= 0.99
    assert "name" in d
    assert "activity" in d
    assert d["text"] or d["name"]


def test_index_company_invalid(vs):
    assert not vs.index_company({})
    assert not vs.index_company({"company_id": "x"})


def test_index_company_valid(vs):
    ok = vs.index_company({"company_id": "x1", "legal_name": "Metal A", "faaliyet": "Celik"})
    assert ok


def test_health(vs_with_rows):
    h = vs_with_rows.health()
    assert h["status"] == "ok"
    assert h["indexed"] == 3
    assert h["pgvector"] is False
    assert "fallback" in h


def test_search_by_ids(vs_with_rows):
    results = vs_with_rows.search_by_ids(["c1", "c3"], query="celik")
    assert len(results) == 2
    ids = {r.id for r in results}
    assert ids == {"c1", "c3"}
