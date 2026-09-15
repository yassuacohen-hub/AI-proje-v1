# -*- coding: utf-8 -*-
"""Veri Tazelik Etiketi — Freshness label ve Manuel Yenileme."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


# Eşikler (dakika)
TAZE_DAKIKA: int = 30
ESKİYE_DAKIKA: int = 120


def tazelik_etiketi(son_guncelleme: datetime | None, simdi: datetime) -> dict:
    """Tazelik etiketi hesapla.

    Args:
        son_guncelleme: Son Güncüllemme zamanı (timezone-aware veya naive) veya None
        simdi: Şimdi anki zaman (timezone-aware veya naive)

    Returns:
        dict: {etiketi, saat_farki, renk}
        - etiketi: 'taze' | 'eskiyor' | 'bayat'
        - saat_farki: dakika cinsinden float (None ise None)
        - renk: 'green' | 'yellow' | 'red' | 'gray'

    Kural:
        son_guncelleme is None → etiketi='bayat', renk='gray', saat_farki=None
        dakika_farkı ≤ 30 → 'taze', 'green'
        dakika_farkı ≤ 120 → 'eskiyor', 'yellow'
        dakika_farkısı > 120 → 'bayat', 'red'
    """
    if son_guncelleme is None:
        return {"etiketi": "bayat", "saat_farki": None, "renk": "gray"}

    # Zaman dilimini birleştir
    if son_guncelleme.tzinfo is None and simdi.tzinfo is not None:
        son_guncelleme = son_guncelleme.replace(tzinfo=simdi.tzinfo)
    elif son_guncelleme.tzinfo is not None and simdi.tzinfo is None:
        simdi = simdi.replace(tzinfo=son_guncelleme.tzinfo)

    fark = son_guncelleme - simdi
    dakika = abs(fark.total_seconds()) / 60.0

    if dakika <= TAZE_DAKIKA:
        return {"etiketi": "taze", "saat_farki": round(dakika, 2), "renk": "green"}
    if dakika <= ESKİYE_DAKIKA:
        return {"etiketi": "eskiyor", "saat_farki": round(dakika, 2), "renk": "yellow"}
    return {"etiketi": "bayat", "saat_farki": round(dakika, 2), "renk": "red"}
