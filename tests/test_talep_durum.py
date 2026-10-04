# -*- coding: utf-8 -*-
"""TSG-05 mandallari: talep durum makinesi + SLA.

Asil risk SLA'de: mesai disi ve hafta sonu TASIMA yanlis olursa musteriye
"10 dakikada teslim" denip gece 03:00'te vadesi gecmis talep uretilir.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.company_master import talep_durum as td


# --- durum makinesi --------------------------------------------------------
def test_baslangic_rezerve_ve_uc_degil() -> None:
    assert td.BASLANGIC_DURUMU == td.REZERVE
    assert td.uc_durum_mu(td.REZERVE) is False


def test_tam_yasam_dongusu_rezerve_isleniyor_tamam() -> None:
    d = td.BASLANGIC_DURUMU
    for hedef in (td.ISLENIYOR, td.TAMAM):
        d = td.gecis_yap(d, hedef)
    assert d == td.TAMAM
    assert td.uc_durum_mu(d) is True


def test_iade_hem_rezerveden_hem_isleniyordan() -> None:
    assert td.gecis_yap(td.REZERVE, td.IADE) == td.IADE
    assert td.gecis_yap(td.ISLENIYOR, td.IADE) == td.IADE


def test_uc_durumdan_cikis_yok() -> None:
    for uc in (td.TAMAM, td.IADE):
        with pytest.raises(ValueError, match="uç durumdur"):
            td.gecis_yap(uc, td.ISLENIYOR)


def test_rezerveden_tamama_atlanamaz() -> None:
    """Islenmeden teslim edilmis talep = olculmemis is."""
    with pytest.raises(ValueError, match="izinli değil"):
        td.gecis_yap(td.REZERVE, td.TAMAM)


@pytest.mark.parametrize("bozuk", ["", "yok", "reserved", "REZERVE ", None, 42])
def test_bilinmeyen_durum_valueerror(bozuk) -> None:  # noqa: ANN001
    if bozuk == "REZERVE ":
        assert td.durum_dogrula(bozuk) == td.REZERVE  # normalize edilir
        return
    with pytest.raises(ValueError):
        td.durum_dogrula(bozuk)


def test_db_esleme_cift_yonlu_ve_tam() -> None:
    for d in td.DURUMLAR:
        assert td.db_degerden(td.db_deger(d)) == d
    with pytest.raises(ValueError):
        td.db_degerden("bilinmeyen")


def test_db_degerleri_ascii_gocteki_check_ile_ayni() -> None:
    """Sema CHECK kisiti ile Python kapisi ayni dort degeri tutmali."""
    assert sorted(td.db_deger(d) for d in td.DURUMLAR) == [
        "done", "processing", "refunded", "reserved",
    ]


# --- SLA -------------------------------------------------------------------
def _an(y: int, ay: int, g: int, s: int, dk: int = 0) -> datetime:
    return datetime(y, ay, g, s, dk, tzinfo=timezone.utc)


def test_mesai_ici_10_dakika() -> None:
    # 2026-09-29 Sali, 14:00 -> mesai ici
    gelis = _an(2026, 9, 29, 14, 0)
    assert td.mesai_icinde_mi(gelis) is True
    assert td.sla_son_teslim(gelis) == _an(2026, 9, 29, 14, 10)


def test_mesai_bitisi_haric_baslangici_dahil() -> None:
    assert td.mesai_icinde_mi(_an(2026, 9, 29, 9, 0)) is True
    assert td.mesai_icinde_mi(_an(2026, 9, 29, 18, 0)) is False


def test_mesai_oncesi_ayni_gun_09_10() -> None:
    """Sali 07:00 gelen talep ayni gun mesai baslayinca islenir, ertesi gune ITMEZ."""
    assert td.sla_son_teslim(_an(2026, 9, 29, 7, 0)) == _an(2026, 9, 29, 9, 10)


def test_mesai_sonrasi_ertesi_is_gunu() -> None:
    """Sali 22:00 -> Carsamba 09:10."""
    assert td.sla_son_teslim(_an(2026, 9, 29, 22, 0)) == _an(2026, 9, 30, 9, 10)


def test_cuma_aksami_pazartesiye_tasinir() -> None:
    # 2026-10-02 Cuma 19:00 -> 2026-10-05 Pazartesi 09:10
    gelis = _an(2026, 10, 2, 19, 0)
    assert gelis.weekday() == 4
    assert td.sla_son_teslim(gelis) == _an(2026, 10, 5, 9, 10)


def test_cumartesi_ogle_pazartesiye_tasinir() -> None:
    # Cumartesi mesai saatinde gelse bile is gunu degil.
    gelis = _an(2026, 10, 3, 14, 0)
    assert gelis.weekday() == 5
    assert td.mesai_icinde_mi(gelis) is False
    assert td.sla_son_teslim(gelis) == _an(2026, 10, 5, 9, 10)


def test_hafta_sonu_is_gunu_degil() -> None:
    assert td.is_gunu_mu(_an(2026, 10, 3, 12, 0).date()) is False  # Cumartesi
    assert td.is_gunu_mu(_an(2026, 10, 4, 12, 0).date()) is False  # Pazar
    assert td.is_gunu_mu(_an(2026, 10, 5, 12, 0).date()) is True   # Pazartesi


def test_sla_asimi_uc_durumda_sayilmaz() -> None:
    gelis = _an(2026, 9, 29, 14, 0)
    gec = _an(2026, 9, 29, 15, 0)
    assert td.sla_asildi_mi(gelis, gec, td.ISLENIYOR) is True
    assert td.sla_asildi_mi(gelis, gec, td.TAMAM) is False
    assert td.sla_asildi_mi(gelis, gec, td.IADE) is False


def test_sla_asimi_sinirda() -> None:
    gelis = _an(2026, 9, 29, 14, 0)
    assert td.sla_asildi_mi(gelis, _an(2026, 9, 29, 14, 10), td.REZERVE) is False
    assert td.sla_asildi_mi(gelis, _an(2026, 9, 29, 14, 11), td.REZERVE) is True


def test_gelis_datetime_olmali() -> None:
    with pytest.raises(ValueError, match="datetime olmalı"):
        td.sla_son_teslim("2026-09-29")  # type: ignore[arg-type]


def test_negatif_sla_reddedilir() -> None:
    with pytest.raises(ValueError, match="negatif"):
        td.sla_son_teslim(_an(2026, 9, 29, 14, 0), sla_dakika=-1)


def test_zaman_dilimi_korunur() -> None:
    """Naive giris naive, aware giris aware kalir; sessiz UTC kaymasi olmaz."""
    assert td.sla_son_teslim(datetime(2026, 9, 29, 14, 0)).tzinfo is None
    assert td.sla_son_teslim(_an(2026, 9, 29, 22, 0)).tzinfo is timezone.utc


def test_tatil_listesi_bos_olculmedigi_icin() -> None:
    """D-268: tatil takvimi olculmedi, kume BOS. Doldurmak urun sahibi girdisi ister."""
    assert td._TATILLER == frozenset(), (
        "Tatil listesi tahminle doldurulmus. Resmi tatil takvimi urun sahibinden "
        "gelmeden yazilmaz (D-268)."
    )
