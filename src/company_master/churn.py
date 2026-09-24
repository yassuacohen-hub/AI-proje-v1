# -*- coding: utf-8 -*-
"""Churn risk skoru (SSOT §9 K1).
PRD P0 — Kural tabanlı, 3 sinyal planlı (giriş+arama+AI).
Şimdilik tek sinyal (last_login) ile başlar; arama/AI log tablosu henüz yok (SSOT §12 G2).
ML'e ileride yüksel (SSOT §9 ilke).

Kural: sinyal = Σ(1 for g in (g_giris,g_arama,g_ai) if g >= 14)
       Çıktı: {0: 'Yok', 1: 'Düşük', 2: 'Orta', 3: 'Yüksek'}

Tek sinyalde (last_login):
- 0 sinyal (son_giris < 14 gün önce) -> 'Yok'
- 1 sinyal (son_giris >= 14 gün veya None) -> 'Düşük'

>>> from datetime import date, timedelta
>>> bugun = date(2026, 9, 24)
>>> risk_etiketi(bugun, bugun)           # Bugün giriş yapmış (< 14 gün)
'Yok'
>>> risk_etiketi(bugun - timedelta(days=13), bugun)  # 13 gün önce (< 14)
'Yok'
>>> risk_etiketi(bugun - timedelta(days=14), bugun)  # 14 gün önce (>= 14)
'Düşük'
>>> risk_etiketi(bugun - timedelta(days=30), bugun)  # 30 gün önce (>= 14)
'Düşük'
>>> risk_etiketi(None, bugun)            # Hiç giriş yok
'Düşük'
"""
from __future__ import annotations

from datetime import date
from typing import Optional


def risk_etiketi(son_giris: Optional[date], bugun: date) -> str:
    """Kullanıcının churn risk etiketini döndürür (SSOT §9 K1).

    Kural: sinyal = 1 if son_giris is None or (bugun - son_giris).days >= 14 else 0
    Çıktı: 0 sinyal -> 'Yok', 1 sinyal -> 'Düşük'
    (3 sinyalle genişleyecek: 0->Yok, 1->Düşük, 2->Orta, 3->Yüksek)
    """
    if son_giris is None:
        return "Düşük"

    gun_farki = (bugun - son_giris).days
    return "Yok" if gun_farki < 14 else "Düşük"


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)