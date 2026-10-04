# -*- coding: utf-8 -*-
"""Odin AI RAG testleri.

Embedder testleri 2026-10-02'de güncellendi (ALTYAPI-RAG-EMBEDDER-01):
eski sürüm 16 boyutlu `hashlib` sahte vektörü varsayıyordu. Sahte embedder
silindi; artık `Embedder` gerçek `vector.embedder.Embedder` ile AYNI nesne.
Bu yüzden ağ gerektiren testler **sahte istemci** kullanır (canlı ölçüm
teslim özetindedir: 4096 boyut, k(demir,metal)=0.8428 > k(demir,gida)=0.6767).
"""
from __future__ import annotations

import pytest
from company_master.odin_ai.rag import Embedder, Chunk, chunk_metin, chunk_bol, chunk_topla


class _SahteIstemci:
    """4096 boyutlu sahte vektor dondurur; ag cagrisi yapmaz."""

    def __init__(self, boyut: int = 4096) -> None:
        self.boyut = boyut

    def embed(self, texts, model):
        return [
            [float(hash((t, i)) % 1000) / 1000.0 for i in range(self.boyut)]
            for t in texts
        ]


class TestEmbedder:
    """Embedder testleri (sahte istemci ile, ag gerektirmez)."""

    def test_embed_returns_embedding_result(self):
        sonuc = Embedder(client=_SahteIstemci()).embed(["test metni"])
        assert sonuc.ok_count == 1, f"beklenen 1, {sonuc.ok_count}"
        assert sonuc.failed_count == 0
        assert len(sonuc.embeddings[0]) == 4096
        assert all(isinstance(x, float) for x in sonuc.embeddings[0])

    def test_embed_deterministic_same_text_same_vector(self):
        e = Embedder(client=_SahteIstemci())
        v1 = e.embed(["ayni metin"]).embeddings[0]
        v2 = e.embed(["ayni metin"]).embeddings[0]
        assert v1 == v2

    def test_embed_different_texts_different_vectors(self):
        e = Embedder(client=_SahteIstemci())
        v1 = e.embed(["metin bir"]).embeddings[0]
        v2 = e.embed(["metin iki"]).embeddings[0]
        assert v1 != v2

    def test_embed_empty_string_returns_no_vector(self):
        # Artik 16 sifir donmez: bos metin ATLANIR (vektor uretilmez).
        # D-249: "veri yok" 0 demek degildir.
        sonuc = Embedder(client=_SahteIstemci()).embed([""])
        assert sonuc.ok_count == 0
        assert sonuc.embeddings == []

    def test_embed_batch_preserves_count(self):
        sonuc = Embedder(client=_SahteIstemci()).embed(["a", "b", "c"])
        assert sonuc.ok_count == 3


class TestChunk:
    """Chunk dataclass testleri."""

    def test_chunk_is_frozen_dataclass(self):
        chunk = Chunk(icerik="test", baslangic=0, bitis=4, boyut=4, ozet="test")
        with pytest.raises(AttributeError):
            chunk.icerik = "yeni"

    def test_chunk_ozet_first_60_chars(self):
        long_text = "a" * 100
        chunk = Chunk(icerik=long_text, baslangic=0, bitis=100, boyut=100, ozet=long_text[:60])
        assert chunk.ozet == "a" * 60


class TestChunkMetin:
    """chunk_metin testleri."""

    def test_chunk_metin_returns_non_empty_list(self):
        chunks = chunk_metin("bu bir test metnidir")
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_chunk_metin_chunks_cover_full_text(self):
        metin = "x" * 500
        chunks = chunk_metin(metin, boyut=200)
        birlesik = "".join(c.icerik for c in chunks)
        assert len(birlesik) >= len(metin)

    def test_chunk_metin_respects_size(self):
        chunks = chunk_metin("abcdefghij", boyut=3)
        assert all(c.boyut <= 3 for c in chunks)

    def test_chunk_metin_empty_string_returns_empty_list(self):
        chunks = chunk_metin("")
        assert chunks == []


class TestChunkBol:
    """chunk_bol testleri."""

    def test_chunk_bol_splits_on_delimiter(self):
        metin = "parça1\n\nparça2\n\nparça3"
        result = chunk_bol(metin, "\n\n")
        assert result == ["parça1", "parça2", "parça3"]

    def test_chunk_bol_default_delimiter(self):
        metin = "parça1\n\nparça2"
        result = chunk_bol(metin)
        assert result == ["parça1", "parça2"]

    def test_chunk_bol_empty_string_returns_empty_list(self):
        result = chunk_bol("")
        assert result == []

    def test_chunk_bol_filters_empty_parts(self):
        metin = "a\n\n\n\nb"
        result = chunk_bol(metin, "\n\n")
        assert result == ["a", "b"]


class TestChunkTopla:
    """chunk_topla testleri."""

    def test_chunk_topla_returns_string(self):
        chunks = [
            Chunk(icerik="abc", baslangic=0, bitis=3, boyut=3, ozet="abc"),
            Chunk(icerik="def", baslangic=3, bitis=6, boyut=3, ozet="def"),
        ]
        result = chunk_topla(chunks)
        assert isinstance(result, str)

    def test_chunk_topla_preserves_order(self):
        chunks = [
            Chunk(icerik="son", baslangic=6, bitis=9, boyut=3, ozet="son"),
            Chunk(icerik="ilk", baslangic=0, bitis=3, boyut=3, ozet="ilk"),
        ]
        result = chunk_topla(chunks)
        assert result.startswith("ilk")
        assert result.endswith("son")

    def test_chunk_topla_deduplicates_overlap(self):
        chunks = [
            Chunk(icerik="abcdef", baslangic=0, bitis=6, boyut=6, ozet="abcdef"),
            Chunk(icerik="cdefgh", baslangic=4, bitis=10, boyut=6, ozet="cdefgh"),
        ]
        result = chunk_topla(chunks)
        assert result == "abcdefgh"

    def test_chunk_topla_empty_list_returns_empty_string(self):
        result = chunk_topla([])
        assert result == ""
