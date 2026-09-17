#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9R-02: Store (ChromaDB fallback) birim testleri - pano/veriye dokunmaz."""
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


def test_store_doc_to_dict():
    doc = VectorDoc(id="x", vector=[1.0, 0.0], metadata={"k": "v"})
    d = doc.to_dict()
    assert d["id"] == "x"
    assert d["vector"] == [1.0, 0.0]
    assert d["metadata"] == {"k": "v"}


def test_store_hit_to_dict():
    hit = SearchHit(id="y", score=0.95, metadata={"k": "v"})
    d = hit.to_dict()
    assert d["id"] == "y"
    assert d["score"] == 0.95
    assert d["metadata"] == {"k": "v"}


def test_cosine_bos():
    from src.company_master.vector.store import _cosine
    assert _cosine([], []) == 0.0
    assert _cosine([1.0], []) == 0.0
    assert _cosine([], [1.0]) == 0.0


def test_cosine_farkli_uzunluk():
    from src.company_master.vector.store import _cosine
    assert _cosine([1.0, 2.0], [1.0]) == 0.0


def test_cosine_sifir_norm():
    from src.company_master.vector.store import _cosine
    assert _cosine([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_cosine_ayni_vektor():
    from src.company_master.vector.store import _cosine
    assert _cosine([3.0, 4.0], [3.0, 4.0]) == 1.0


def test_store_upsert_bos():
    store = EmbeddedVectorStore()
    assert store.upsert([]) == 0


def test_store_count_fallback(monkeypatch):
    store = EmbeddedVectorStore()
    store.upsert([VectorDoc(id="x", vector=_v(1.0), metadata={})])

    class FakeColl:
        def count(self):
            raise RuntimeError("boom")
        def delete(self, **kw):
            pass

    store._coll = FakeColl()
    store._in_memory = False
    assert store.count() == 1


def test_store_query_chromadb_yol():
    store = EmbeddedVectorStore()
    store.upsert([VectorDoc(id="a", vector=_v(1.0), metadata={"osb": "ostim"}),
                   VectorDoc(id="b", vector=_v(0.9), metadata={"osb": "bas_kent"})])

    class FakeRes:
        def get(self, key, default=None):
            if key == "ids": return [["a"]]
            if key == "distances": return [[0.5]]
            if key == "metadatas": return [[{"osb": "ostim"}]]
            return default

    class FakeColl:
        def query(self, **kwargs):
            return FakeRes()
        def count(self):
            return 2
        def delete(self, **kw):
            pass

    store._coll = FakeColl()
    store._in_memory = False
    hits = store.query(_v(1.0), top_k=5, where={"osb": "ostim"})
    assert len(hits) == 1
    assert hits[0].id == "a"
    assert hits[0].score == 0.5


def test_store_collection_chromadb_olustur(monkeypatch):
    import types as _types
    from unittest.mock import MagicMock

    mock_chromadb = _types.ModuleType("chromadb")
    client_mock = MagicMock()
    coll_mock = MagicMock()
    client_mock.get_or_create_collection.return_value = coll_mock
    mock_chromadb.Client = MagicMock(return_value=client_mock)

    monkeypatch.setattr("src.company_master.vector.store.chromadb", mock_chromadb, raising=False)
    monkeypatch.setattr("src.company_master.vector.store.CHROMADB_AVAILABLE", True, raising=False)

    store = EmbeddedVectorStore()
    assert store._in_memory is False
    coll = store.collection
    assert coll is coll_mock
    assert client_mock.get_or_create_collection.called


def test_store_upsert_chromadb_yol(monkeypatch):
    import types as _types
    from unittest.mock import MagicMock

    fake_coll = MagicMock()
    fake_coll.upsert.return_value = None

    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = fake_coll
    mock_chromadb = _types.ModuleType("chromadb")
    mock_chromadb.Client = MagicMock(return_value=mock_client)

    monkeypatch.setattr("src.company_master.vector.store.chromadb", mock_chromadb, raising=False)
    monkeypatch.setattr("src.company_master.vector.store.CHROMADB_AVAILABLE", True, raising=False)

    store = EmbeddedVectorStore()
    assert store._in_memory is False
    store.upsert([VectorDoc(id="a", vector=[1.0]*1536, metadata={"k": "v1"})])
    fake_coll.upsert.assert_called_once()


def test_store_query_hata_fallback(monkeypatch):
    import types as _types
    from unittest.mock import MagicMock

    fake_coll = MagicMock()
    fake_coll.query.side_effect = RuntimeError("db boom")

    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = fake_coll
    mock_chromadb = _types.ModuleType("chromadb")
    mock_chromadb.Client = MagicMock(return_value=mock_client)

    monkeypatch.setattr("src.company_master.vector.store.chromadb", mock_chromadb, raising=False)
    monkeypatch.setattr("src.company_master.vector.store.CHROMADB_AVAILABLE", True, raising=False)

    store = EmbeddedVectorStore()
    store.upsert([VectorDoc(id="a", vector=[1.0]*1536, metadata={"k": "v"})])
    hits = store.query([1.0]*1536, top_k=5)
    assert hits == []


def test_store_delete_all_chromadb(monkeypatch):
    import types as _types
    from unittest.mock import MagicMock

    fake_coll = MagicMock()
    fake_coll.delete.return_value = None

    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = fake_coll
    mock_chromadb = _types.ModuleType("chromadb")
    mock_chromadb.Client = MagicMock(return_value=mock_client)

    monkeypatch.setattr("src.company_master.vector.store.chromadb", mock_chromadb, raising=False)
    monkeypatch.setattr("src.company_master.vector.store.CHROMADB_AVAILABLE", True, raising=False)

    store = EmbeddedVectorStore()
    store.upsert([VectorDoc(id="a", vector=[1.0]*1536, metadata={})])
    store.delete_all()
    fake_coll.delete.assert_called_once()
