# -*- coding: utf-8 -*-
"""VEC-TEST-01: Intelligence vektor testleri icin izolasyon.

`VectorSearch` altinda `EmbeddedVectorStore` kullanilir. CI'da gercek
`chromadb` kurulu oldugu icin koleksiyon testler arasinda paylasilir ve
`indexed` sayilari kayar. In-memory fallback'e zorlayarak deterministik
davranis saglanir.
"""
from __future__ import annotations

import pytest

from src.company_master.vector import store as store_mod


@pytest.fixture(autouse=True)
def _vektor_in_memory(monkeypatch):
    """Her testte in-memory fallback (paylasilan chromadb koleksiyonu yok)."""
    monkeypatch.setattr(store_mod, "CHROMADB_AVAILABLE", False, raising=False)
    monkeypatch.setattr(store_mod, "chromadb", None, raising=False)
    yield
