# -*- coding: utf-8 -*-
"""D-249 / D-256: Firma ilişki ağı — Faz 3 Entity Graph (VERI-ENTITY-GRAPH-01).

Tek yazma kapısı `kenarlari_yaz()`'dır. Bu pakette başka bir yazıcı yoktur.

SSOT: `yedekler/Huginn Data Insights (HUGIns).txt:756-774` (10 düğüm türü),
`:779` ("Şirket ekosistemini görselleştirmek."), `:837-839` ("Şirket ağ
haritası."), `:859-861` (Faz 3 = Entity Graph).

v0 KAPSAMI: yalnız 2 kenar türü ÜRETİLİR — `same_osb` ve `nace_complementary`.
Kalan 9 tür şemada kanonik listede vardır ama KAYNAK VERİ YOKTUR, boş bırakılır
(D-249: boş ≠ yok sayılmış). Kanıt olmayan kenar yazılmaz.
"""
from __future__ import annotations

from .kenarlar import (
    EDGE_TYPES,
    EDGE_TYPES_V0,
    KANONIK_EDGE_TYPES,
    KENAR,
    KenarHatasi,
    STRENGTH_ARALIK,
    kenarlari_yaz,
    normalize,
    nace_tamamlayici,
    osb_komsulari,
)

__all__ = [
    "EDGE_TYPES",
    "EDGE_TYPES_V0",
    "KANONIK_EDGE_TYPES",
    "KENAR",
    "KenarHatasi",
    "STRENGTH_ARALIK",
    "kenarlari_yaz",
    "normalize",
    "nace_tamamlayici",
    "osb_komsulari",
]
