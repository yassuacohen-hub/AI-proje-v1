#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9R-02: Embedder unit testleri (mock client; gercek 9Router cagirmaz)."""
from __future__ import annotations

import pytest

from src.company_master.vector.embedder import Embedder, EmbeddingResult, embed_texts

class MockClient:
    """Basit mock: embed(liste, model) -> [[0.1, 0.2], ...]"""

    def __init__(self, vektor_sayisi: int = 0, hata_sayisi: int = 0) -> None:
        self.cagri = 0
        self.vektor_sayisi = vektor_sayisi  # 0 = gelen liste kadar
        self.hata_sayisi = hata_sayisi      # ilk N cagrıda raise

    def embed(self, texts: list[str], model: str = "") -> list[list[float]]:
        self.cagri += 1
        if self.cagri <= self.hata_sayisi:
            raise RuntimeError("gecici gateway hatasi (VPN?)")
        if self.vektor_sayisi:
            return [[0.1, 0.2, 0.3] for _ in range(self.vektor_sayisi)]
        return [[0.1, 0.2, 0.3] for _ in texts]


def test_embed_basit():
    embedder = Embedder(client=MockClient(), batch_size=2)
    res = embedder.embed(["a", "b", "c"])
    assert isinstance(res, EmbeddingResult)
    assert res.ok_count == 3
    assert res.failed_count == 0
    assert len(res.embeddings[0]) == 3


def test_embed_bos_giris():
    embedder = Embedder(client=MockClient())
    res = embedder.embed([])
    assert res.ok_count == 0
    res2 = embedder.embed(["  ", ""])
    assert res2.ok_count == 0


def test_embed_retry_sonra_basari():
    # ilk 2 cagrı hata, 3.su basarili (max_retries=3)
    embedder = Embedder(client=MockClient(hata_sayisi=2), batch_size=4, max_retries=3,
                        retry_delay_s=0.0)
    res = embedder.embed(["x", "y"])
    assert res.ok_count == 2
    assert res.failed_count == 0


def test_embed_batch_tukenince_hata():
    # surekli hata -> chunk errors'a eklenir, kismi basari korunur
    embedder = Embedder(client=MockClient(hata_sayisi=999), batch_size=2,
                        max_retries=2, retry_delay_s=0.0)
    res = embedder.embed(["a", "b", "c", "d"])
    assert res.ok_count == 0
    assert res.failed_count == 4
    assert any("VPN" in d for _, d in res.errors)


def test_embed_sistem_hatasi_hizli_fail_retry_yok():
    """Istemci kurulu degil (sistem hatasi) -> 1 hata kaydi, retry beklenmez."""

    class YokClient:
        def embed(self, texts, model=""):
            raise RuntimeError(
                "9Router istemcisi kurulu degil; once .env'de NINEROUTER_* "
                "ve requirements kurulumu gerekli."
            )

    embedder = Embedder(client=YokClient(), batch_size=2, max_retries=3,
                        retry_delay_s=0.0)
    res = embedder.embed(["a", "b", "c", "d"])
    assert res.ok_count == 0
    assert res.failed_count == 4
    assert all("kurulu degil" in d for _, d in res.errors)


def test_embed_sonuc_dict_ve_embeddings_ayristir():
    """Client dict donerse embeddings anahtari kullanilir."""

    class DictClient:
        def embed(self, texts, model=""):
            return {"embeddings": [[0.0, 0.1] for _ in texts], "model": model}

    embedder = Embedder(client=DictClient())
    res = embedder.embed(["a"])
    assert res.ok_count == 1

def test_embed_to_dict():
    result = EmbeddingResult(
        embeddings=[[1.0, 2.0], [3.0, 4.0]],
        model="test",
        errors=[(0, "fail")],
    )
    d = result.to_dict()
    assert d["model"] == "test"
    assert d["ok"] == 2
    assert d["failed"] == 1
    assert d["dim"] == 2
    assert d["errors"] == [{"index": 0, "detail": "fail"}]


def test_embedder_client_uyuzsuz(monkeypatch):
    monkeypatch.setattr("src.company_master.vector.embedder.get_client", None, raising=False)
    embedder = Embedder(client=None, batch_size=2, max_retries=1, retry_delay_s=0)
    with pytest.raises(RuntimeError, match="kurulu degil"):
        _ = embedder.client


def test_embed_texts_fonksiyon():
    result = embed_texts(["a", "b"], batch_size=1, client=MockClient())
    assert result.ok_count == 2
    assert isinstance(result.model, str)
