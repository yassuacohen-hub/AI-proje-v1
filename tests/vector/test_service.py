#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9R-02: VectorService + firma_metni + dublikasyon testleri."""
from __future__ import annotations

import pytest

from src.company_master.vector.service import firma_metni, VectorService, DuplicateGroup
from src.company_master.vector.embedder import Embedder
from src.company_master.vector.store import EmbeddedVectorStore, VectorDoc


class SabitEmbedder(Embedder):
    """Sabit vektor donen embedder (koordinat bazli: bazi textler benzer)."""

    def embed(self, texts, **kw):
        from src.company_master.vector.embedder import EmbeddingResult
        vecs = []
        errs = []
        for i, t in enumerate(texts):
            t = (t or "").lower()
            if "metal" in t or "çelik" in t:
                vecs.append([1.0, 0.0, 0.0])       # metal grubu
            elif "plastik" in t:
                vecs.append([0.0, 1.0, 0.0])       # plastik grubu
            else:
                vecs.append([0.0, 0.0, 1.0])
        return EmbeddingResult(embeddings=vecs, model="test", errors=errs)


@pytest.fixture
def svc():
    store = EmbeddedVectorStore()  # in-memory
    return VectorService(embedder=SabitEmbedder(), store=store)


def test_firma_metni_birlesimi():
    row = {"legal_name": "ABC Metal Sanayi", "faaliyet": "Çelik üretim",
           "nace_code": 24, "vkn": "123"}
    text = firma_metni(row)
    assert "ABC Metal Sanayi" in text
    assert "Çelik üretim" in text
    assert "24" in text


def test_firma_metni_bozuk_deger():
    row = {"legal_name": "-", "faaliyet": "yok"}
    assert firma_metni(row) == ""


def test_index_firmalar_ve_arama(svc):
    rows = [{"company_id": "c1", "legal_name": "ABC Metal Sanayi",
             "faaliyet": "Çelik üretim"},
            {"company_id": "c2", "legal_name": "XYZ Plastik",
             "faaliyet": "Plastik enjeksiyon"},
            {"company_id": "c3", "legal_name": "DEF Metal İşleme",
             "faaliyet": "Çelik sac"}]
    n = svc.index_firmalar(rows)
    assert n == 3
    assert svc.store.count() == 3

    hits = svc.find_similar("çelik metal üretim", top_k=2)
    assert len(hits) == 2
    assert hits[0].id in {"c1", "c3"}  # metal grubu en yakin


def test_deduplicate_by_vkn(svc):
    rows = [
        {"company_id": "g1a", "legal_name": "ABC Metal", "faaliyet": "Çelik", "vkn": "111"},
        {"company_id": "g1b", "legal_name": "ABC Metal Sanayi", "faaliyet": "Çelik üretim", "vkn": "111"},
        {"company_id": "g2", "legal_name": "Farkli Firma", "faaliyet": "Plastik", "vkn": "222"},
        {"company_id": "g3", "legal_name": "VKNsiz", "faaliyet": "Yok", "vkn": ""},
    ]
    gruplar = svc.deduplicate_by_vkn(rows)
    assert len(gruplar) == 1  # yalniz VKN=111 iki kayit
    g = gruplar[0]
    assert isinstance(g, DuplicateGroup)
    assert g.vkn == "111"
    assert len(g.ids) == 2
    assert len(g.scores) == 1  # tek cift
    assert g.scores[0] > 0.99  # metal+çelik ayni vektor


def test_deduplicate_vkn_yok(svc):
    rows = [{"company_id": "a", "legal_name": "X", "vkn": ""},
            {"company_id": "b", "legal_name": "Y", "vkn": "555"}]
    assert svc.deduplicate_by_vkn(rows) == []

def test_firma_metni_liste_deger():
    row = {"legal_name": "ABC", "faaliyet": ["Çelik", "Demir"]}
    text = firma_metni(row)
    assert "ABC" in text
    assert "Çelik" in text
    assert "Demir" in text


def test_degistirme_grubu_to_dict():
    g = DuplicateGroup(vkn="111", ids=["a", "b"], scores=[0.99], texts=["x"])
    d = g.to_dict()
    assert d["vkn"] == "111"
    assert d["ids"] == ["a", "b"]
    assert d["scores"] == [0.99]
    assert d["texts"] == ["x"]


def test_index_firmalar_bos_embed(svc):
    EmbeddingResult = __import__("src.company_master.vector.embedder", fromlist=["EmbeddingResult"]).EmbeddingResult
    bos_embedder = type("BosEmbedder", (Embedder,), {
        "embed": lambda self, texts, **kw: EmbeddingResult(embeddings=[], model="test", errors=[])
    })
    svc2 = VectorService(embedder=bos_embedder(), store=svc.store)
    assert svc2.index_firmalar([{"company_id": "x", "legal_name": "Y"}]) == 0


def test_find_similar_bos_embed(svc):
    EmbeddingResult = __import__("src.company_master.vector.embedder", fromlist=["EmbeddingResult"]).EmbeddingResult
    bos_embedder = type("BosEmbedder", (Embedder,), {
        "embed": lambda self, texts, **kw: EmbeddingResult(embeddings=[], model="test", errors=[])
    })
    svc2 = VectorService(embedder=bos_embedder(), store=svc.store)
    assert svc2.find_similar("anything") == []


def test_find_similar_top_k_fazla(svc):
    svc.index_firmalar([
        {"company_id": "c1", "legal_name": "ABC Metal Sanayi", "faaliyet": "Çelik üretim"},
        {"company_id": "c2", "legal_name": "XYZ Plastik", "faaliyet": "Plastik enjeksiyon"},
        {"company_id": "c3", "legal_name": "DEF Metal İşleme", "faaliyet": "Çelik sac"},
    ])
    hits = svc.find_similar("çelik metal üretim", top_k=100)
    assert len(hits) == 3


def test_embed_document(svc):
    doc = VectorDoc(id="doc1", vector=[1.0, 0.0, 0.0], metadata={"text": "çelik metal"})
    svc.embed_document(doc)
    assert svc.store.count() >= 1


def test_deduplicate_by_vkn_bos_embed(svc):
    EmbeddingResult = __import__("src.company_master.vector.embedder", fromlist=["EmbeddingResult"]).EmbeddingResult
    bos_embedder = type("BosEmbedder", (Embedder,), {
        "embed": lambda self, texts, **kw: EmbeddingResult(embeddings=[], model="test", errors=[])
    })
    svc2 = VectorService(embedder=bos_embedder(), store=svc.store)
    rows = [{"company_id": "a", "vkn": "111"}, {"company_id": "b", "vkn": "111"}]
    assert svc2.deduplicate_by_vkn(rows) == []


def test_index_firmalar_id_key_degisken(svc):
    rows = [{"id": "custom-1", "legal_name": "Test", "faaliyet": "X"}]
    n = svc.index_firmalar(rows, id_key="id")
    assert n == 1


def test_index_firmalar_else_yol(monkeypatch):
    monkeypatch.setattr("src.company_master.vector.service.tracer", None)
    svc2 = VectorService(embedder=SabitEmbedder(), store=EmbeddedVectorStore())
    assert svc2.tracer is None
    rows = [
        {"company_id": "c1", "legal_name": "ABC Metal", "faaliyet": "Çelik"},
        {"company_id": "c2", "legal_name": "XYZ Plastik", "faaliyet": "Plastik"},
    ]
    n = svc2.index_firmalar(rows)
    assert n == 2
    assert svc2.store.count() == 2


def test_find_similar_else_yol(monkeypatch):
    monkeypatch.setattr("src.company_master.vector.service.tracer", None)
    svc2 = VectorService(embedder=SabitEmbedder(), store=EmbeddedVectorStore())
    svc2.index_firmalar([
        {"company_id": "c1", "legal_name": "ABC Metal", "faaliyet": "Çelik"},
    ])
    hits = svc2.find_similar("çelik", top_k=5)
    assert len(hits) == 1


def test_deduplicate_else_yol(monkeypatch):
    monkeypatch.setattr("src.company_master.vector.service.tracer", None)
    svc2 = VectorService(embedder=SabitEmbedder(), store=EmbeddedVectorStore())
    rows = [
        {"company_id": "g1a", "legal_name": "ABC Metal", "faaliyet": "Çelik", "vkn": "111"},
        {"company_id": "g1b", "legal_name": "ABC Metal Sanayi", "faaliyet": "Çelik üretim", "vkn": "111"},
        {"company_id": "g2", "legal_name": "Farkli", "faaliyet": "Plastik", "vkn": "222"},
    ]
    gruplar = svc2.deduplicate_by_vkn(rows)
    assert len(gruplar) == 1
    assert gruplar[0].vkn == "111"


def test_embed_document_bos_embed(monkeypatch):
    monkeypatch.setattr("src.company_master.vector.service.tracer", None)
    EmbeddingResult = __import__("src.company_master.vector.embedder", fromlist=["EmbeddingResult"]).EmbeddingResult
    bos_embedder = type("BosEmbedder", (Embedder,), {
        "embed": lambda self, texts, **kw: EmbeddingResult(embeddings=[], model="test", errors=[])
    })
    svc2 = VectorService(embedder=bos_embedder(), store=EmbeddedVectorStore())
    doc = VectorDoc(id="doc1", vector=[1.0, 0.0, 0.0], metadata={"text": "test"})
    svc2.embed_document(doc)
    assert svc2.store.count() == 0
