# -*- coding: utf-8 -*-
"""9R-02: Vektor katmani paketi.

9Router embed + ChromaDB saklama + semantik benzerlik/dublikasyon.
Katman sorumlulugu (dokuman 9ROUTER_SEMANTIK_KATMAN_MIMARISI.md, bolum 3):
  - Apify (kaynak) -> 9Router embed (vektorlestirme) -> ChromaDB (saklama)
    -> matcher (dublikasyon/il e-e match karari)
"""
from .embedder import Embedder, EmbeddingResult, embed_texts
from .store import EmbeddedVectorStore, SearchHit, VectorDoc
from .service import VectorService, DuplicateGroup, firma_metni

__all__ = [
    "Embedder",
    "EmbeddingResult",
    "embed_texts",
    "EmbeddedVectorStore",
    "SearchHit",
    "VectorDoc",
    "VectorService",
    "DuplicateGroup",
    "firma_metni",
]