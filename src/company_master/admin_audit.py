# -*- coding: utf-8 -*-
"""Şüpheli Aktivite Tespit Kuralları (SSOT §9 K10, §10 sıra 11, §12 G9).

Tespit-only: otomatik hesap kilitleme/bildirim DAHIL DEĞIL.
Saf fonksiyonlar — DB erişimi yok, olay listesi parametre olarak alınır.

Kurallar (3 sinyal):
1. supheli_basarisiz_giris: 5 dakikada >5 başarısız giriş
2. supheli_cok_ulkeli_ip: 24 saatte >2 farklı ülke
3. supheli_gece_toplu_export: 00:00-06:00 UTC arası toplu export

Zaman dilimi: TIMESTAMPTZ üzerinden UTC hesaplanır. Gece penceresi 00:00-06:00 UTC.
Ülke kodu None olan kayıt farklı ülke sayılmaz (eksik veri şüphe üretmez).

>>> from datetime import datetime, timedelta, timezone
>>> from admin_audit import (
...     supheli_basarisiz_giris, supheli_cok_ulkeli_ip, supheli_gece_toplu_export,
...     supheli_skor, supheli_etiket
... )
>>>
>>> # Sabit zaman dilimi (UTC)
>>> utc = timezone.utc
>>> now = datetime(2026, 9, 24, 12, 0, 0, tzinfo=utc)
>>>
>>> # Boş liste -> tüm kurallar False, skor 0
>>> supheli_basarisiz_giris([], now=now)
False
>>> supheli_cok_ulkeli_ip([], now=now)
False
>>> supheli_gece_toplu_export([], now=now)
False
>>> supheli_skor([])
0
>>> supheli_etiket(0)
'Temiz'
>>>
>>> # supheli_basarisiz_giris: 5 dakikada 5+ başarısız giriş
>>> olaylar = [
...     {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=i), "detay": {}}
...     for i in range(6)  # 6 başarısız giriş
... ]
>>> supheli_basarisiz_giris(olaylar, now=now, pencere_dk=5, esik=5)
True
>>>
>>> # Eşik 5, 5 başarısız -> False (sadece >5)
>>> olaylar_5 = olaylar[:5]
>>> supheli_basarisiz_giris(olaylar_5, now=now, pencere_dk=5, esik=5)
False
>>>
>>> # supheli_cok_ulkeli_ip: 24 saatte 2+ farklı ülke
>>> olaylar_ulkeler = [
...     {"olay_zamani": now - timedelta(hours=i), "detay": {"ulke_kodu": "TR"}}
...     for i in range(1, 4)  # TR, TR, TR -> 1 ülke
... ] + [
...     {"olay_zamani": now - timedelta(hours=5), "detay": {"ulke_kodu": "DE"}},
...     {"olay_zamani": now - timedelta(hours=8), "detay": {"ulke_kodu": "FR"}},
... ]  # 3 farklı ülke: TR, DE, FR
>>> supheli_cok_ulkeli_ip(olaylar_ulkeler, now=now, pencere_saat=24, esik=2)
True
>>>
>>> # Sadece 1 ülke -> False
>>> olaylar_tek_ulke = [
...     {"olay_zamani": now - timedelta(hours=i), "detay": {"ulke_kodu": "TR"}}
...     for i in range(1, 4)
... ]
>>> supheli_cok_ulkeli_ip(olaylar_tek_ulke, now=now, pencere_saat=24, esik=2)
False
>>>
>>> # Ülke kodu None -> sayılmaz
>>> olaylar_none_ulke = [
...     {"olay_zamani": now - timedelta(hours=1), "detay": {"ulke_kodu": "TR"}},
...     {"olay_zamani": now - timedelta(hours=2), "detay": {"ulke_kodu": None}},
... ]
>>> supheli_cok_ulkeli_ip(olaylar_none_ulke, now=now, pencere_saat=24, esik=1)
False
>>>
>>> # supheli_gece_toplu_export: 00:00-06:00 UTC arası export
>>> gece = datetime(2026, 9, 24, 3, 30, 0, tzinfo=utc)
>>> olaylar_gece = [
...     {"olay_tipi": "export", "olay_zamani": gece, "detay": {}}
... ]
>>> supheli_gece_toplu_export(olaylar_gece, now=gece, baslangic_saat=0, bitis_saat=6, esik=1)
True
>>>
>>> # 06:00 -> gece penceresi dışında (bitiş saat dahil değil)
>>> sabah = datetime(2026, 9, 24, 6, 0, 0, tzinfo=utc)
>>> olaylar_sabah = [
...     {"olay_tipi": "export", "olay_zamani": sabah, "detay": {}}
... ]
>>> supheli_gece_toplu_export(olaylar_sabah, now=sabah, baslangic_saat=0, bitis_saat=6, esik=1)
False
>>>
>>> # 05:59 -> gece penceresi içinde
>>> gece_son = datetime(2026, 9, 24, 5, 59, 0, tzinfo=utc)
>>> olaylar_gece_son = [
...     {"olay_tipi": "export", "olay_zamani": gece_son, "detay": {}}
... ]
>>> supheli_gece_toplu_export(olaylar_gece_son, now=gece_son, baslangic_saat=0, bitis_saat=6, esik=1)
True
>>>
>>> # supheli_skor + supheli_etiket
>>> olaylar_test = [
...     {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=1), "detay": {}},
...     {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=2), "detay": {}},
...     {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=3), "detay": {}},
...     {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=4), "detay": {}},
...     {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=5), "detay": {}},
...     {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(seconds=30), "detay": {}},
... ]
>>> skor = supheli_skor(olaylar_test, now=now)
>>> skor
1
>>> supheli_etiket(skor)
'İzle'
>>>
>>> supheli_etiket(0)
'Temiz'
>>> supheli_etiket(1)
'İzle'
>>> supheli_etiket(2)
'Şüpheli'
>>> supheli_etiket(3)
'Kritik'
>>> supheli_etiket(4)
'Kritik'
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

# ---- Eşik Sabitleri (Modül Sabiti + Parametre) ----

# 5 dakikada >5 başarısız giriş
BASARISIZ_GIRIS_PENCERE_DK: int = 5
BASARISIZ_GIRIS_ESIK: int = 5

# 24 saatte >2 farklı ülke
COK_ULKELI_PENCERE_SAAT: int = 24
COK_ULKELI_ESIK: int = 2

# Gece 00:00-06:00 UTC, export esik >=1
GECE_EXPORT_BASLANGIC_SAAT: int = 0
GECE_EXPORT_BITIS_SAAT: int = 6
GECE_EXPORT_ESIK: int = 1

# Etiket haritası
ETIKET_HARITASI: dict[int, str] = {
    0: "Temiz",
    1: "İzle",
    2: "Şüpheli",
    3: "Kritik",
}


def _olay_zamani_al(olay: dict[str, Any]) -> datetime:
    """Olaydan olay_zamani'ı datetime olarak çıkar (UTC normalize)."""
    zamani = olay.get("olay_zamani")
    if isinstance(zamani, str):
        # ISO format string -> datetime (UTC varsay)
        return datetime.fromisoformat(zamani.replace("Z", "+00:00"))
    if isinstance(zamani, datetime):
        # timezone-aware ise UTC'ye çevir, naive ise UTC varsay
        if zamani.tzinfo is not None:
            return zamani.astimezone(timezone.utc)
        return zamani.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def _ulke_kodu_al(olay: dict[str, Any]) -> str | None:
    """Olayın detay JSONB'ından ülke kodunu çıkar."""
    detay = olay.get("detay")
    if isinstance(detay, dict):
        return detay.get("ulke_kodu")
    if isinstance(detay, str):
        import json
        try:
            return json.loads(detay).get("ulke_kodu")
        except (json.JSONDecodeError, TypeError):
            return None
    return None


def _pencere_baslangic(now: datetime, dakika: int = 0, saat: int = 0) -> datetime:
    """Zaman penceresinin başlangıcı (UTC)."""
    delta = timedelta(minutes=dakika, hours=saat)
    return now - delta


def supheli_basarisiz_giris(
    olaylar: list[dict[str, Any]],
    *,
    now: datetime | None = None,
    pencere_dk: int = BASARISIZ_GIRIS_PENCERE_DK,
    esik: int = BASARISIZ_GIRIS_ESIK,
) -> bool:
    """5 dakikada >5 başarısız giriş tespiti.

    Kural: olay_tipi='giris' AND basarili=False olan olaylar, son N dakikada sayılır.
    Eşik: >esik (ör. >5 yani 6+).

    Args:
        olaylar: Olay listesi (her biri: olay_tipi, basarili, olay_zamani).
        now: Referans zamanı (UTC, timezone-aware). None ise şimdi (UTC).
        pencere_dk: Dakika cinsinden zaman penceresi (varsayılan 5).
        esik: Eşik sayısı (varsayılan 5). >esik olduğu için True döner.

    Returns:
        bool: Şüpheli başarısız giriş tespit edildiyse True.
    """
    if not olaylar:
        return False

    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    else:
        now = now.astimezone(timezone.utc)

    pencere_bas = now - timedelta(minutes=pencere_dk)

    sayac = 0
    for olay in olaylar:
        if olay.get("olay_tipi") != "giris":
            continue
        if olay.get("basarili") is True:
            continue

        olay_zamani = _olay_zamani_al(olay)
        if olay_zamani >= pencere_bas:
            sayac += 1

    return sayac > esik


def supheli_cok_ulkeli_ip(
    olaylar: list[dict[str, Any]],
    *,
    now: datetime | None = None,
    pencere_saat: int = COK_ULKELI_PENCERE_SAAT,
    esik: int = COK_ULKELI_ESIK,
) -> bool:
    """24 saatte >2 farklı ülke kodu tespiti.

    Kural: Farklı ülke kodları (ulke_kodu) sayısı son N saatte >esik.
    - ulke_kodu None olan kayıtlar SAYILMAZ (eksik veri şüphe üretmez).
    - Zaman penceresi UTC üzerinden.

    Args:
        olaylar: Olay listesi (her biri: olay_zamani, detay->ulke_kodu).
        now: Referans zamanı (UTC, timezone-aware). None ise şimdi (UTC).
        pencere_saat: Saat cinsinden zaman penceresi (varsayılan 24).
        esik: Farklı ülke sayısı eşiği (varsayılan 2). >esik olduğu için True döner.

    Returns:
        bool: Şüpheli çok ülkeli IP tespit edildiyse True.
    """
    if not olaylar:
        return False

    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    else:
        now = now.astimezone(timezone.utc)

    pencere_bas = now - timedelta(hours=pencere_saat)

    ulkeler = set()
    for olay in olaylar:
        olay_zamani = _olay_zamani_al(olay)
        if olay_zamani < pencere_bas:
            continue

        ulke = _ulke_kodu_al(olay)
        if ulke:  # None boş string değilse say
            ulkeler.add(ulke)

    return len(ulkeler) > esik


def supheli_gece_toplu_export(
    olaylar: list[dict[str, Any]],
    *,
    now: datetime | None = None,
    baslangic_saat: int = GECE_EXPORT_BASLANGIC_SAAT,
    bitis_saat: int = GECE_EXPORT_BITIS_SAAT,
    esik: int = GECE_EXPORT_ESIK,
) -> bool:
    """00:00-06:00 UTC arası toplu export tespiti.

    Kural: olay_tipi='export' olan olaylar, UTC 00:00-06:00 aralığında.
    - Zaman penceresi UTC saat diliminde (baslangic_saat dahil, bitis_saat hariç).
    - Eşik: >=esik (varsayılan 1) export olayı.

    Args:
        olaylar: Olay listesi (her biri: olay_tipi, olay_zamani).
        now: Referans zamanı (UTC, timezone-aware). None ise şimdi (UTC).
        baslangic_saat: Gece penceresi başlangıç saati UTC (varsayılan 0, dahil).
        bitis_saat: Gece penceresi bitiş saati UTC (varsayılan 6, hariç).
        esik: Export sayısı eşiği (varsayılan 1). >=esik olduğu için True döner.

    Returns:
        bool: Şüpheli gece export tespit edildiyse True.
    """
    if not olaylar:
        return False

    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    else:
        now = now.astimezone(timezone.utc)

    # Gece penceresi: bugün 00:00 - 06:00 UTC
    gun_bas = now.replace(hour=0, minute=0, second=0, microsecond=0)
    pencere_bas = gun_bas + timedelta(hours=baslangic_saat)
    pencere_bit = gun_bas + timedelta(hours=bitis_saat)

    sayac = 0
    for olay in olaylar:
        if olay.get("olay_tipi") != "export":
            continue

        olay_zamani = _olay_zamani_al(olay)
        if pencere_bas <= olay_zamani < pencere_bit:
            sayac += 1

    return sayac >= esik


def supheli_skor(
    olaylar: list[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> int:
    """Şüpheli skor: tetiklenen kural sayısı (0-3).

    Args:
        olaylar: Olay listesi.
        now: Referans zamanı (UTC).

    Returns:
        int: Tetiklenen kural sayısı (0-3).
    """
    skor = 0
    if supheli_basarisiz_giris(olaylar, now=now):
        skor += 1
    if supheli_cok_ulkeli_ip(olaylar, now=now):
        skor += 1
    if supheli_gece_toplu_export(olaylar, now=now):
        skor += 1
    return skor


def supheli_etiket(skor: int) -> str:
    """Skor -> etiket haritası.

    0 -> 'Temiz'
    1 -> 'İzle'
    2 -> 'Şüpheli'
    3 -> 'Kritik'
    4+ -> 'Kritik'

    Args:
        skor: supheli_skor çıktısı.

    Returns:
        str: Risk etiketi.
    """
    return ETIKET_HARITASI.get(skor, "Kritik")


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
