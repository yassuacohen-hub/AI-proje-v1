# -*- coding: utf-8 -*-
"""Paket → haber kaynağı kapısı (PAKET_KOTA_TASARIMI §4, BORC-PLAN-ALANI-01). DB yok."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from company_master.paketler import (  # noqa: E402
    PAKET_KAYNAKLARI,
    VARSAYILAN_KAYNAKLAR,
    _ORJINAL_SIRALAMA,
    paket_kaynaklari,
)


def test_her_fiyat_tierinin_kaynak_haritasi_var():
    assert set(PAKET_KAYNAKLARI) == set(_ORJINAL_SIRALAMA)


def test_ust_paket_alttakini_kapsar():
    for alt, ust in zip(_ORJINAL_SIRALAMA, _ORJINAL_SIRALAMA[1:]):
        assert set(PAKET_KAYNAKLARI[alt]) <= set(PAKET_KAYNAKLARI[ust]), f"{ust} {alt}'i kapsamıyor"


def test_paketsiz_firma_varsayilan_alir():
    assert paket_kaynaklari([]) == frozenset(VARSAYILAN_KAYNAKLAR)


def test_bilinmeyen_paket_kapiyi_acmaz():
    assert paket_kaynaklari(["Premium", "yok"]) == frozenset(VARSAYILAN_KAYNAKLAR)


def test_birden_fazla_paket_birlesir():
    k = paket_kaynaklari(["Temel", "Standart"])
    assert "linkedin" in k and "instagram" not in k
