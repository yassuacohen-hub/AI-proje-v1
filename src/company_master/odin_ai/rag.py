# -*- coding: utf-8 -*-
"""Odin AI RAG iskeleti — Chunk ve metin parçalama.

Embedder BURADA TANIMLANMAZ. Gerçek embedder `company_master.vector.embedder`
modülündedir; iki embedder birden D-211 ikiz yapısı yaratırdı. Geriye dönük
uyumluluk için `Embedder` / `EmbeddingResult` / `embed_texts` oradan dışa
aktarılır (gövde kopyalanmaz — D-230).

SSOT: `yedekler/Huginn Data Insights (HUGIns).txt:760-774`, :779, :837-839.
KÖPRÜ (D-184): görev plans/brief_yasu_ALTYAPI-RAG-EMBEDDER-01.md
· test tests/test_rag_embedder.py · hub hubs/TOOLS_SCRIPTS_HUB.md
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

# D-230: gövde kopyalanmaz, isim korunur (D-211 ikiz yapı yasağı).
from ..vector.embedder import Embedder, EmbeddingResult, embed_texts  # noqa: F401


@dataclass(frozen=True)
class Chunk:
    """Metin parçası (chunk) veri sınıfı."""
    icerik: str
    baslangic: int
    bitis: int
    boyut: int
    ozet: str


@dataclass(frozen=True)
class Chunk:
    """Metin parçası (chunk) veri sınıfı."""
    icerik: str
    baslangic: int
    bitis: int
    boyut: int
    ozet: str


def chunk_metin(metin: str, boyut: int = 200) -> List[Chunk]:
    """Metni örtüşen parçalara (chunk) böler."""
    if not metin:
        return []

    if boyut <= 0:
        raise ValueError("boyut pozitif olmalıdır")

    chunklar = []
    adim = max(1, boyut // 2)

    for baslangic in range(0, len(metin), adim):
        bitis = min(baslangic + boyut, len(metin))
        icerik = metin[baslangic:bitis]

        if not icerik:
            break

        chunk = Chunk(
            icerik=icerik,
            baslangic=baslangic,
            bitis=bitis,
            boyut=len(icerik),
            ozet=icerik[:60]
        )
        chunklar.append(chunk)

        if bitis >= len(metin):
            break

    return chunklar


def chunk_bol(metin: str, ayrac: str = "\n\n") -> List[str]:
    """Metni ayraca göre böler."""
    if not metin:
        return []

    parcalar = metin.split(ayrac)
    return [p for p in parcalar if p]


def chunk_topla(chunklar: List[Chunk]) -> str:
    """Chunk'ları birleştirir, örtüşen bölgeleri tekilleştirir."""
    if not chunklar:
        return ""

    chunklar_sirali = sorted(chunklar, key=lambda c: c.baslangic)
    n = len(chunklar_sirali)

    sonuc_parcalari = []

    for i, chunk in enumerate(chunklar_sirali):
        # Bu chunk'tan alınacak orijinal metin aralığı
        start_orig = chunk.baslangic
        end_orig = chunk.bitis

        # Önceki chunk ile örtüşme: önceki chunk'un bitişinden başla
        if i > 0:
            prev_bitis = chunklar_sirali[i - 1].bitis
            start_orig = max(start_orig, prev_bitis)

        # Sonraki chunk ile örtüşme: sonraki chunk'un başlangıcında bitir
        if i < n - 1:
            next_baslangic = chunklar_sirali[i + 1].baslangic
            end_orig = min(end_orig, next_baslangic)

        # Chunk içindeki indekslere çevir
        start_idx = start_orig - chunk.baslangic
        end_idx = end_orig - chunk.baslangic

        if start_idx < len(chunk.icerik) and end_idx > start_idx:
            sonuc_parcalari.append(chunk.icerik[start_idx:end_idx])

    return "".join(sonuc_parcalari)
