# -*- coding: utf-8 -*-
"""9R-02: VectorService — yuksek seviye semantik islemler.

Firma kayitlarini vektorlestirip store'a yazar ve benzerlik/dublikasyon
sorgulari yapar. Bu katman `entity_resolution/matcher.py` tarafindan
vektor skoru saglamak icin kullanilir.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Iterable

from .embedder import Embedder
from .store import EmbeddedVectorStore, SearchHit, VectorDoc

logger = logging.getLogger(__name__)

# Firma metnine cevrilecek kayit alanlari (varsa)
_FIRMA_ALANLARI = (
    "legal_name", "unvan", "firma_adi", "company_name", "name",
    "faaliyet_konusu", "faaliyet", "description", "is_alani", "sektor",
    "nace_kodu", "nace_code",
)


def firma_metni(row: dict[str, Any]) -> str:
    """Firma kaydindan semantik arama icin tek metin uretir."""
    parts: list[str] = []
    for key in _FIRMA_ALANLARI:
        val = row.get(key)
        if val is None:
            continue
        if isinstance(val, (list, tuple)):
            val = ", ".join(str(v) for v in val if v)
        val = str(val).strip()
        if val and val.lower() not in ("-", "yok", "none", "n/a"):
            parts.append(val)
    return " | ".join(parts)


@dataclass
class DuplicateGroup:
    """Ayni VKN / benzer unvanli firma grubu."""
    vkn: str
    ids: list[str]
    scores: list[float]
    texts: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "vkn": self.vkn,
            "ids": self.ids,
            "scores": [round(s, 6) for s in self.scores],
            "texts": self.texts,
        }


class VectorService:
    """Embed + store + benzerlik sorgusu tek noktasi."""

    def __init__(
        self,
        embedder: Embedder | None = None,
        store: EmbeddedVectorStore | None = None,
    ) -> None:
        self.embedder = embedder or Embedder()
        self.store = store or EmbeddedVectorStore()

    def embed_document(self, doc: VectorDoc) -> None:
        """Tek dokumani vektorle ve store'a yaz."""
        result = self.embedder.embed([doc.metadata.get("text", "") or "firma"])
        if not result.embeddings:
            return
        doc.vector = result.embeddings[0]
        self.store.upsert([doc])

    def index_firmalar(
        self,
        rows: Iterable[dict[str, Any]],
        id_key: str = "company_id",
    ) -> int:
        """Firma satirlarini embed + store'a toplu yazar.

        Her satir icin id = row[id_key] (yoksa index). metadata'ya
        firma bilgileri + indexlenmis text konur.
        """
        items = list(rows)
        metinler = [firma_metni(r) for r in items]
        result = self.embedder.embed(metinler)
        if not result.embeddings:
            logger.warning("Embed sonucu bos; hicbir firma indexlenmedi. %s",
                           result.to_dict())
            return 0

        docs: list[VectorDoc] = []
        for i, row in enumerate(items):
            fid = str(row.get(id_key) or row.get("id") or f"row-{i}")
            meta = {
                "firm_id": fid,
                "text": metinler[i],
                "nace_code": row.get("nace_code") or row.get("nace_kodu") or "",
                "osb_region": row.get("osb_region") or row.get("bolge") or "",
                "verification_status": row.get("verification_status") or "unknown",
                "last_updated": row.get("last_updated") or "",
            }
            for k, v in row.items():
                if k not in meta and not isinstance(v, (dict, list)):
                    meta[k] = str(v)[:200]
            docs.append(VectorDoc(id=fid, vector=result.embeddings[i], metadata=meta))

        self.store.upsert(docs)
        logger.info("%d firma indexlendi (model=%s)", len(docs), result.model)
        return len(docs)

    def find_similar(
        self,
        text: str,
        top_k: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[SearchHit]:
        """Metin sorgusunu embedleyip en benzer firmalari dondurur."""
        result = self.embedder.embed([text])
        if not result.embeddings:
            return []
        return self.store.query(result.embeddings[0], top_k=top_k, where=where)

    def deduplicate_by_vkn(
        self,
        rows: Iterable[dict[str, Any]],
        id_key: str = "company_id",
        vkn_key: str = "vkn",
    ) -> list[DuplicateGroup]:
        """Ayni VKN'yi paylasan firmalari gruplar ve semantik skorlar.

        Geri donus: her grup icin o grup icindeki tum ciftlerin ortalama
        cosine benzerligi (score) — boylece 'ayni VKN ama farkli firma'
        olanlar dusuk skorla, gercek dupliketler yuksek skorla cikar.
        """
        groups: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            vkn = str(row.get(vkn_key) or "").strip()
            if not vkn:
                continue
            groups.setdefault(vkn, []).append(row)

        out: list[DuplicateGroup] = []
        for vkn, grup in groups.items():
            if len(grup) < 2:
                continue
            # once index (grup icin sadece embed)
            metinler = [firma_metni(r) for r in grup]
            result = self.embedder.embed(metinler)
            if not result.embeddings:
                continue
            ids = [
                str(r.get(id_key) or r.get("id") or f"row-{i}")
                for i, r in enumerate(grup)
            ]
            scores = _cift_skorlari(result.embeddings)
            out.append(
                DuplicateGroup(
                    vkn=vkn, ids=ids, scores=scores, texts=metinler
                )
            )
        return out


def _cift_skorlari(vecs: list[list[float]]) -> list[float]:
    """Grup vektorlerinin tum cift cosine skorlarini dondurur (sirali)."""
    from .store import _cosine

    scores: list[float] = []
    n = len(vecs)
    for a in range(n):
        for b in range(a + 1, n):
            scores.append(_cosine(vecs[a], vecs[b]))
    scores.sort(reverse=True)
    return scores