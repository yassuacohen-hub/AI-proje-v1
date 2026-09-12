#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9R-02: Store (ChromaDB fallback) unit testleri — pano/veriye dokunmaz."""
from __future__ import annotations

import math

import pytest

from src.company_master.vector.store import EmbeddedVectorStore, VectorDoc, SearchHit


def _v(v: float) -> list[float]:
    """1-boyutlu vektor (test icin kosinus hesaplar basit olsun)."""
    return [v, 0.0, 0.0]


def test_store_upsert_ve_count():
    store = EmbeddedVectorStore()  # in-memory fallback (chromadb yoksa)
    n = store.upsert([VectorDoc(id="a1", vector=_v(1.0), metadata={"x": 1}),
                      VectorDoc(id="a2", vector=_v(0.5), metadata={"x": 2})])
    assert n == 2
    assert store.count() == 2


def test_store_query_en_yakin():
    store = EmbeddedVectorStore()
    store.upsert([
        VectorDoc(id="benzer", vector=[1.0, 0.0, 0.0], metadata={"name": "benzer"}),
        # uzak vektor soru vektoruyle neredeyse dik -> dusuk cosine
        VectorDoc(id="uzak", vector=[0.1, 1.0, 0.0], metadata={"name": "uzak"}),
    ])
    hits = store.query([1.0, 0.0, 0.0], top_k=2)
    assert len(hits) == 2
    assert isinstance(hits[0], SearchHit)
    assert hits[0].id == "benzer"
    assert hits[0].score > hits[1].score


def test_store_query_where_filtresi():
    store = EmbeddedVectorStore()
    store.upsert([
        VectorDoc(id="a", vector=_v(1.0), metadata={"osb": "ostim"}),
        VectorDoc(id="b", vector=_v(0.9), metadata={"osb": "bas_kent"}),
    ])
    hits = store.query(_v(1.0), top_k=5, where={"osb": "ostim"})
    assert [h.id for h in hits] == ["a"]


def test_store_kosinus_calismasi():
    """Kosinus benzerligi: ayni vektor->1, ortogonal->0."""
    store = EmbeddedVectorStore()
    store.upsert([VectorDoc(id="k", vector=[1.0, 0.0, 0.0], metadata={}),
                  VectorDoc(id="d", vector=[0.0, 1.0, 0.0], metadata={})])
    hits = store.query([1.0, 0.0, 0.0], top_k=2)
    scores = {h.id: h.score for h in hits}
    assert scores["k"] > 0.99
    assert scores["d"] < 0.05


def test_store_bos_query():
    store = EmbeddedVectorStore()
    assert store.query([1.0, 0.0]) == []


def test_store_delete_all():
    store = EmbeddedVectorStore()
    store.upsert([VectorDoc(id="x", vector=_v(1.0), metadata={})])
    store.delete_all()
    assert store.count() == 0