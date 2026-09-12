# -*- coding: utf-8 -*-
"""9R-02: EmbeddedVectorStore — ChromaDB sarmalayici.

Vektorleri ChromaDB koleksiyonunda saklar ve cosine benzerligi + metadata
filtresi ile sorgular. ChromaDB yoksa (optional dep) basit in-memory
fallback devreye girer — boylece matcher ve testler bagimsiz calisir.

V9 3.3 ChromaDB Vector Architecture referansi:
  collections: capabilities, products, tender_specs, hs_code_mappings
  metadata:    firm_id, nace_code, osb_region, verification_status, last_updated
"""
from __future__ import annotations

import logging
import os
import math
from dataclasses import dataclass, field
from typing import Any, Iterable

logger = logging.getLogger(__name__)

# Boyut yalniz bilgi amacli; asil dogrulama ilk insert'te yapilir.
DEFAULT_DIM = 1536

try:
    import chromadb  # type: ignore
    CHROMADB_AVAILABLE = True
except ImportError:  # pragma: no cover
    chromadb = None  # type: ignore[assignment]
    CHROMADB_AVAILABLE = False

# OpenTelemetry tracing
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

if OTEL_AVAILABLE:
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    jaeger_host = os.getenv("JAEGER_HOST", "localhost")
    jaeger_port = int(os.getenv("JAEGER_PORT", "6831"))
    jaeger_exporter = JaegerExporter(
        agent_host_name=jaeger_host,
        agent_port=jaeger_port,
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    RequestsInstrumentor().instrument()
else:
    tracer = None



@dataclass
class VectorDoc:
    """Saklanacak vektor + metadata."""
    id: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "vector": self.vector, "metadata": self.metadata}


@dataclass
class SearchHit:
    """Benzerlik sorgusu sonucu tek hit."""
    id: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "score": round(self.score, 6), "metadata": self.metadata}


class EmbeddedVectorStore:
    """ChromaDB tabanli vektor deposu (in-memory fallback ile)."""

    def __init__(
        self,
        collection_name: str = "companies",
        persist_dir: str | None = None,
        dimension: int = DEFAULT_DIM,
        chroma_client: Any | None = None,
    ) -> None:
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.dimension = dimension
        self._chroma_client = chroma_client
        self._coll: Any | None = None
        self._memory: dict[str, VectorDoc] = {}
        self._in_memory = not CHROMADB_AVAILABLE and chroma_client is None
        self.tracer = tracer
        if self._in_memory:
            logger.info(
                "ChromaDB kurulu degil; in-memory fallback kullanilacak "
                "(semantik katman sinirli, VKN+fuzzy devam eder)."
            )

    # ---- yaplandi ----
    @property
    def collection(self) -> Any:
        if self._coll is not None:
            return self._coll
        if self._in_memory:
            return None
        client = self._chroma_client
        if client is None:
            if chromadb is None:
                self._in_memory = True
                return None
            kwargs: dict[str, Any] = {}
            if self.persist_dir:
                kwargs["path"] = self.persist_dir
            client = chromadb.Client(**kwargs)
            self._chroma_client = client
        try:
            self._coll = client.get_or_create_collection(name=self.collection_name)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "ChromaDB koleksiyon olusturulamadi; in-memory fallback: %s", exc
            )
            self._in_memory = True
        return self._coll

    # ---- yazma ----
    def upsert(self, docs: Iterable[VectorDoc]) -> int:
        if self.tracer is not None:
            with self.tracer.start_as_current_span("EmbeddedVectorStore.upsert"):
                        """Dokumanlari koleksiyona yazar; eklenen sayisini dondurur."""
                        items = list(docs)
                        if not items:
                            return 0
                        coll = self.collection
                        if coll is None:
                            # in-memory fallback
                            for d in items:
                                self._memory[d.id] = d
                            return len(items)
                
                        # boyut kontrolu (ilk gorselde dogrula)
                        dim = len(items[0].vector)
                        if dim != self.dimension:
                            logger.warning(
                                "Boyut uyumsuz: beklenen %d, gelen %d — %d ile devam",
                                self.dimension, dim, dim,
                            )
                        self._dim = dim
                
                        coll.upsert(
                            ids=[d.id for d in items],
                            embeddings=[d.vector for d in items],
                            metadatas=[d.metadata for d in items],
                        )
                        return len(items)
                
                    # ---- sorgulama ----
        else:
            """Dokumanlari koleksiyona yazar; eklenen sayisini dondurur."""
            items = list(docs)
            if not items:
                return 0
            coll = self.collection
            if coll is None:
                # in-memory fallback
                for d in items:
                    self._memory[d.id] = d
                return len(items)
    
            # boyut kontrolu (ilk gorselde dogrula)
            dim = len(items[0].vector)
            if dim != self.dimension:
                logger.warning(
                    "Boyut uyumsuz: beklenen %d, gelen %d — %d ile devam",
                    self.dimension, dim, dim,
                )
            self._dim = dim
    
            coll.upsert(
                ids=[d.id for d in items],
                embeddings=[d.vector for d in items],
                metadatas=[d.metadata for d in items],
            )
            return len(items)
    
        # ---- sorgulama ----
    def query(
        self,
        vector: list[float],
        top_k: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[SearchHit]:
        """Cosine benzerligine gore en yakin top_k kaydi dondurur."""
        coll = self.collection
        if coll is None:
            return self._query_memory(vector, top_k, where)
        try:
            res = coll.query(
                query_embeddings=[vector],
                n_results=top_k,
                where=where,
                include=["metadatas", "distances"],
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("ChromaDB sorgu hatasi; memory fallback: %s", exc)
            return self._query_memory(vector, top_k, where)

        hits: list[SearchHit] = []
        ids = res.get("ids", [[]])[0]
        dists = res.get("distances", [[]])[0]
        metas = res.get("metadatas", [{}])[0]
        for doc_id, dist, meta in zip(ids, dists, metas):
            # chroma distance'i cosine distance; score = 1 - distance
            score = max(0.0, min(1.0, 1.0 - float(dist)))
            hits.append(SearchHit(id=doc_id, score=score, metadata=meta or {}))
        return hits

    def _query_memory(
        self,
        vector: list[float],
        top_k: int,
        where: dict[str, Any] | None,
    ) -> list[SearchHit]:
        """In-memory fallback: brute-force cosine."""
        scored: list[SearchHit] = []
        for doc in self._memory.values():
            if where:
                ok = all(doc.metadata.get(k) == v for k, v in where.items())
                if not ok:
                    continue
            sim = _cosine(vector, doc.vector)
            scored.append(SearchHit(id=doc.id, score=sim, metadata=doc.metadata))
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:top_k]

    def count(self) -> int:
        coll = self.collection
        if coll is None:
            return len(self._memory)
        try:
            return coll.count()
        except Exception:  # noqa: BLE001
            return len(self._memory)

    def delete_all(self) -> None:
        coll = self.collection
        if coll is None:
            self._memory.clear()
            return
        coll.delete(where={})
        self._memory.clear()


def _cosine(a: list[float], b: list[float]) -> float:
    """Cosine benzerligi (0..1)."""
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))
