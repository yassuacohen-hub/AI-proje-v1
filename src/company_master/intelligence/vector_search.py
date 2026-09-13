# -*- coding: utf-8 -*-
"""P7-23: Vector Search — üretim kalitesinde benzerlik arama endpointi.

Embedding generation pipeline + similarity search endpoint.
Supabase pgvector hazir destegi (ChromaDB fallback ile calisir).

Kullanim:
    from src.company_master.intelligence.vector_search import VectorSearch

    vs = VectorSearch()
    results = vs.search("çelik üretim", top_k=5)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Iterable
from pathlib import Path

from src.company_master.vector.service import (
    VectorService,
    SearchHit,
    firma_metni,
)
from src.company_master.vector.embedder import Embedder
from src.company_master.vector.store import EmbeddedVectorStore

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 5
MAX_TOP_K = 100


@dataclass
class VectorSearchConfig:
    """VectorSearch ayarlari."""

    top_k: int = DEFAULT_TOP_K
    where: dict[str, Any] | None = None
    id_key: str = "company_id"
    text_fields: tuple[str, ...] = (
        "legal_name",
        "unvan",
        "firma_adi",
        "company_name",
        "name",
        "faaliyet_konusu",
        "faaliyet",
        "description",
        "is_alani",
        "sektor",
        "nace_kodu",
        "nace_code",
    )


class VectorSearch:
    """Firma kayitlari uzerinden vektor benzerlik arama endpointi.

    Pipeline:
      1. Metin cikarma (firma_metni)
      2. Embedding generation (Embedder)
      3. Similarity search (VectorService.find_similar)
      4. Sonuon dondurme (VectorSearchResult)

    pgvector destegi: store katmaninda yoneticilir.
    ChromaDB yoksa in-memory fallback devreye girer.
    """

    def __init__(
        self,
        embedder: Embedder | None = None,
        store: EmbeddedVectorStore | None = None,
        config: VectorSearchConfig | None = None,
    ) -> None:
        self.service = VectorService(
            embedder=embedder,
            store=store,
        )
        self.config = config or VectorSearchConfig()

    def search(
        self,
        query: str,
        top_k: int | None = None,
        where: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Firma kayitlarinda benzerlik arama yapar."""
        if not query or not query.strip():
            return []

        top_k = min(max(1, top_k or self.config.top_k), MAX_TOP_K)
        filter_ = where or self.config.where

        hits = self.service.find_similar(
            text=query,
            top_k=top_k,
            where=filter_,
        )
        return [self._hit_to_result(h) for h in hits]

    def search_by_ids(
        self,
        ids: Iterable[str],
        query: str | None = None,
        top_k: int | None = None,
    ) -> list[VectorSearchResult]:
        """Belirli ID'lere bagli firmalarda arama yapar."""
        if query is None:
            return []
        id_set = set(str(i) for i in ids)
        results = self.search(query=query, top_k=MAX_TOP_K)
        return [r for r in results if r.id in id_set][:top_k or MAX_TOP_K]

    def index_company(self, row: dict[str, Any]) -> bool:
        """Tek firma kayidini vektorle indexler."""
        try:
            text = firma_metni(row)
            if not text:
                return False
            from src.company_master.vector.service import VectorDoc
            doc = VectorDoc(
                id=str(row.get(self.config.id_key) or row.get("id") or ""),
                vector=[],
                metadata={
                    "text": text,
                    **{k: row.get(k, "") for k in self.config.text_fields},
                },
            )
            self.service.embed_document(doc)
            return True
        except Exception as exc:
            logger.warning("index_company hata: %s", exc)
            return False

    def index_companies(
        self,
        rows: Iterable[dict[str, Any]],
    ) -> int:
        """Firma satirlarini toplu indexler."""
        count = self.service.index_firmalar(rows, id_key=self.config.id_key)
        logger.info("VectorSearch: %d firma indexlendi", count)
        return count

    def health(self) -> dict[str, Any]:
        """Servis sagligi kontrolu."""
        return {
            "status": "ok",
            "indexed": self.service.store.count(),
            "pgvector": False,
            "fallback": "in-memory" if hasattr(self.service.store, "_in_memory") and self.service.store._in_memory else "chroma",
        }

    def _hit_to_result(self, hit: SearchHit) -> VectorSearchResult:
        meta = hit.metadata or {}
        return VectorSearchResult(
            id=hit.id,
            score=hit.score,
            name=meta.get("legal_name") or meta.get("name") or "",
            nace=meta.get("nace_code") or meta.get("nace_kodu") or "",
            activity=meta.get("faaliyet") or meta.get("faaliyet_konusu") or "",
            text=meta.get("text", ""),
        )


@dataclass
class VectorSearchResult:
    """Benzerlik arama sonucu."""

    id: str
    score: float
    name: str = ""
    nace: str = ""
    activity: str = ""
    text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "score": round(self.score, 6),
            "name": self.name,
            "nace": self.nace,
            "activity": self.activity,
            "text": self.text[:200] if self.text else "",
        }
