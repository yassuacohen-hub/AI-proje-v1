# -*- coding: utf-8 -*-
"""Odin AI RAG testleri."""
from __future__ import annotations

import pytest
from company_master.odin_ai.rag import Embedder, Chunk, chunk_metin, chunk_bol, chunk_topla


class TestEmbedder:
    """Embedder testleri."""
    
    def test_embed_returns_list_of_float_length_16(self):
        embedder = Embedder()
        result = embedder.embed("test metni")
        assert isinstance(result, list)
        assert len(result) == 16
        assert all(isinstance(x, float) for x in result)
    
    def test_embed_deterministic_same_text_same_vector(self):
        embedder = Embedder()
        v1 = embedder.embed("aynı metin")
        v2 = embedder.embed("aynı metin")
        assert v1 == v2
    
    def test_embed_different_texts_different_vectors(self):
        embedder = Embedder()
        v1 = embedder.embed("metin bir")
        v2 = embedder.embed("metin iki")
        assert v1 != v2
    
    def test_embed_empty_string_returns_zeros(self):
        embedder = Embedder()
        result = embedder.embed("")
        assert result == [0.0] * 16
    
    def test_embed_custom_dimension(self):
        embedder = Embedder(boyut=8)
        result = embedder.embed("test")
        assert len(result) == 8


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
