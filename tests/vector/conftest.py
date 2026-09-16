# -*- coding: utf-8 -*-
"""VEC-TEST-01: Vektor testleri icin izolasyon.

CI ortaminda gercek `chromadb` kurulu oldugundan `EmbeddedVectorStore()`
varsayilan olarak global/paylasilan `companies` koleksiyonunu kullanir;
testler birbirinin verisini gorur ve `chromadb >= 0.5` bos metadata'yi
reddeder. Bu fixture tum vektor testlerini deterministik in-memory
fallback'e zorlar (lokal + CI ayni davranis).
"""
from __future__ import annotations

import pytest

from src.company_master.vector import store as store_mod


@pytest.fixture(autouse=True)
def _vektor_in_memory(monkeypatch):
    """Her testte in-memory fallback: paylasilan koleksiyon kirlenmesi olmasin."""
    monkeypatch.setattr(store_mod, "CHROMADB_AVAILABLE", False, raising=False)
    monkeypatch.setattr(store_mod, "chromadb", None, raising=False)
    yield
