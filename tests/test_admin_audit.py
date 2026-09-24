#!/usr/bin/env python3
"""Admin Audit Testleri — API-ADMIN-SUPHELI-AKTIVITE-21"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone

from company_master.admin_audit import (
    supheli_basarisiz_giris,
    supheli_cok_ulkeli_ip,
    supheli_gece_toplu_export,
    supheli_skor,
    supheli_etiket,
)


def test_supheli_basarisiz_giris_basarili():
    """5 dakikada >5 başarısız giriş tespiti."""
    utc = timezone.utc
    now = datetime(2026, 9, 24, 12, 0, 0, tzinfo=utc)

    # 6 başarısız giriş (0-5 dakika arası)
    olaylar = [
        {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=i), "detay": {}}
        for i in range(6)
    ]
    assert supheli_basarisiz_giris(olaylar, now=now, pencere_dk=5, esik=5) is True

    # 5 başarısız -> eşik değil (>5)
    olaylar_5 = olaylar[:5]
    assert supheli_basarisiz_giris(olaylar_5, now=now, pencere_dk=5, esik=5) is False

    # Boş liste
    assert supheli_basarisiz_giris([], now=now) is False

    # Pencere dışındaki olay sayılmaz
    olaylar_eski = [
        {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=10), "detay": {}}
        for _ in range(10)
    ]
    assert supheli_basarisiz_giris(olaylar_eski, now=now, pencere_dk=5, esik=5) is False


def test_supheli_cok_ulkeli_ip():
    """24 saatte >2 farklı ülke tespiti."""
    utc = timezone.utc
    now = datetime(2026, 9, 24, 12, 0, 0, tzinfo=utc)

    # 3 farklı ülke -> >2 esik
    olaylar = [
        {"olay_zamani": now - timedelta(hours=1), "detay": {"ulke_kodu": "TR"}},
        {"olay_zamani": now - timedelta(hours=2), "detay": {"ulke_kodu": "DE"}},
        {"olay_zamani": now - timedelta(hours=3), "detay": {"ulke_kodu": "FR"}},
    ]
    assert supheli_cok_ulkeli_ip(olaylar, now=now, pencere_saat=24, esik=2) is True

    # 2 ülke -> esik 2, >2 değil
    olaylar_2 = [
        {"olay_zamani": now - timedelta(hours=1), "detay": {"ulke_kodu": "TR"}},
        {"olay_zamani": now - timedelta(hours=2), "detay": {"ulke_kodu": "DE"}},
    ]
    assert supheli_cok_ulkeli_ip(olaylar_2, now=now, pencere_saat=24, esik=2) is False

    # 1 ülke
    olaylar_1 = [
        {"olay_zamani": now - timedelta(hours=1), "detay": {"ulke_kodu": "TR"}},
    ]
    assert supheli_cok_ulkeli_ip(olaylar_1, now=now, pencere_saat=24, esik=1) is False

    # None ülke kodu sayılmaz
    olaylar_none = [
        {"olay_zamani": now - timedelta(hours=1), "detay": {"ulke_kodu": "TR"}},
        {"olay_zamani": now - timedelta(hours=2), "detay": {"ulke_kodu": None}},
    ]
    assert supheli_cok_ulkeli_ip(olaylar_none, now=now, pencere_saat=24, esik=1) is False

    # Boş liste
    assert supheli_cok_ulkeli_ip([], now=now) is False

    # Pencere dışı
    olaylar_eski = [
        {"olay_zamani": now - timedelta(hours=25), "detay": {"ulke_kodu": "TR"}},
        {"olay_zamani": now - timedelta(hours=26), "detay": {"ulke_kodu": "DE"}},
        {"olay_zamani": now - timedelta(hours=26), "detay": {"ulke_kodu": "FR"}},
    ]
    assert supheli_cok_ulkeli_ip(olaylar_eski, now=now, pencere_saat=24, esik=2) is False


def test_supheli_gece_toplu_export():
    """00:00-06:00 UTC arası toplu export."""
    utc = timezone.utc

    # 03:30 -> gece penceresi içinde
    gece = datetime(2026, 9, 24, 3, 30, 0, tzinfo=timezone.utc)
    olaylar = [{"olay_tipi": "export", "olay_zamani": gece, "detay": {}}]
    assert supheli_gece_toplu_export(olaylar, now=gece, baslangic_saat=0, bitis_saat=6, esik=1) is True

    # 06:00 -> bitiş saat dahil değil
    sabah = datetime(2026, 9, 24, 6, 0, 0, tzinfo=timezone.utc)
    olaylar_sabah = [{"olay_tipi": "export", "olay_zamani": sabah, "detay": {}}]
    assert supheli_gece_toplu_export(olaylar_sabah, now=sabah, baslangic_saat=0, bitis_saat=6, esik=1) is False

    # 05:59 -> gece penceresi içinde
    gece_son = datetime(2026, 9, 24, 5, 59, 0, tzinfo=timezone.utc)
    olaylar_gece_son = [{"olay_tipi": "export", "olay_zamani": gece_son, "detay": {}}]
    assert supheli_gece_toplu_export(olaylar_gece_son, now=gece_son, baslangic_saat=0, bitis_saat=6, esik=1) is True

    # Olay tipi export değil
    olaylar_diger = [{"olay_tipi": "giris", "olay_zamani": gece, "detay": {}}]
    assert supheli_gece_toplu_export(olaylar_diger, now=gece, baslangic_saat=0, bitis_saat=6, esik=1) is False

    # Boş liste
    assert supheli_gece_toplu_export([], now=gece) is False

    # Esik 2, 1 export -> False
    assert supheli_gece_toplu_export([{"olay_tipi": "export", "olay_zamani": gece, "detay": {}}], now=gece, baslangic_saat=0, bitis_saat=6, esik=2) is False


def test_supheli_skor_ve_etiket():
    """Skor ve etiket hesaplama."""
    utc = timezone.utc
    now = datetime(2026, 9, 24, 12, 0, 0, tzinfo=utc)

    # Boş liste -> skor 0
    assert supheli_skor([], now=now) == 0
    assert supheli_etiket(0) == "Temiz"

    # Sadece başarısız giriş kuralı tetiklenir
    olaylar = [
        {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=i), "detay": {}}
        for i in range(5)
    ] + [
        {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(seconds=30), "detay": {}}
    ]
    skor = supheli_skor(olaylar, now=now)
    assert skor == 1
    assert supheli_etiket(skor) == "İzle"

    # 2 kural -> Şüpheli
    assert supheli_etiket(2) == "Şüpheli"
    assert supheli_etiket(3) == "Kritik"
    assert supheli_etiket(4) == "Kritik"  # 3+ -> Kritik


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
