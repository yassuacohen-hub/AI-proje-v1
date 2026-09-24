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


def _gun_farki_veya_bayat(son_tarih: Optional[date], bugun: date) -> int:
    """Yardımcı: sinyal 1 mi 0 mu?

    None veya >=14 gün -> 1 (bayat/riskli)
    <14 gün -> 0 (taze)
    """
    if son_tarih is None:
        return 1
    gun_farki = (bugun - son_tarih).days
    return 1 if gun_farki >= 14 else 0


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


def risk_etiketi_3sinyal(
    son_giris: Optional[date],
    son_arama: Optional[date],
    son_ai: Optional[date],
    bugun: date,
) -> str:
    """3-sinyalli churn risk etiketi (SSOT §9 K1 genişletilmiş).

    Sinyaller (her biri 14 gün eşiği):
    - son_giris: son giriş tarihi
    - son_arama: son arama tarihi (user_activity_log.olay_tipi='arama')
    - son_ai: son AI kullanım tarihi (user_activity_log.olay_tipi='ai_kullanim')

    Kural: sinyal = Σ(1 for g in (g_giris, g_arama, g_ai) if g >= 14)
    Çıktı: {0: 'Yok', 1: 'Düşük', 2: 'Orta', 3: 'Yüksek'}

    None girdi = o sinyalde hiç aktivite yok = riskli (1 sayılır).

    >>> from datetime import date, timedelta
    >>> bugun = date(2026, 9, 24)
    >>> # 3 sinyal de taze (<14 gün)
    >>> risk_etiketi_3sinyal(bugun, bugun, bugun, bugun)
    'Yok'
    >>> # 3 sinyal de bayat (>=14 gün)
    >>> risk_etiketi_3sinyal(bugun - timedelta(days=20), bugun - timedelta(days=15), bugun - timedelta(days=30), bugun)
    'Yüksek'
    >>> # Karışık: giriş taze, arama bayat, AI hiç yok = 2 riskli sinyal
    >>> risk_etiketi_3sinyal(bugun, bugun - timedelta(days=20), None, bugun)
    'Orta'
    >>> # Hepsi None (hiç aktivite yok)
    >>> risk_etiketi_3sinyal(None, None, None, bugun)
    'Yüksek'
    >>> # Sadece giriş bayat
    >>> risk_etiketi_3sinyal(bugun - timedelta(days=20), bugun, bugun, bugun)
    'Düşük'
    """
    sinyaller = [
        _gun_farki_veya_bayat(son_giris, bugun),
        _gun_farki_veya_bayat(son_arama, bugun),
        _gun_farki_veya_bayat(son_ai, bugun),
    ]
    toplam = sum(sinyaller)

    ETIKET_MAP = {
        0: "Yok",
        1: "Düşük",
        2: "Orta",
        3: "Yüksek",
    }
    return ETIKET_MAP.get(toplam, "Yüksek")


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
