# -*- coding: utf-8 -*-
"""PO-BACK-03: Kampanya durum makinesi testleri (parametrik)."""
from __future__ import annotations

import itertools

import pytest

from company_master import kampanya_durum as kd

IZINLI = [
    ("taslak", "planlandı"),
    ("taslak", "iptal"),
    ("planlandı", "aktif"),
    ("planlandı", "iptal"),
    ("aktif", "duraklatıldı"),
    ("aktif", "tamamlandı"),
    ("aktif", "iptal"),
    ("duraklatıldı", "aktif"),
    ("duraklatıldı", "iptal"),
]
IZINLI_SET = set(IZINLI)
YASAK = [
    (m, h) for m, h in itertools.product(kd.DURUMLAR, repeat=2)
    if (m, h) not in IZINLI_SET
]


# --- izinli geçişler -------------------------------------------------------
@pytest.mark.parametrize(("mevcut", "hedef"), IZINLI)
def test_izinli_gecis_hedefi_doner(mevcut: str, hedef: str) -> None:
    assert kd.gecis_yap(mevcut, hedef) == hedef
    assert kd.gecis_izinli_mi(mevcut, hedef) is True


# --- yasak geçişler (kendine geçiş + uç durumlardan çıkış dâhil) ----------
@pytest.mark.parametrize(("mevcut", "hedef"), YASAK)
def test_yasak_gecis_valueerror(mevcut: str, hedef: str) -> None:
    with pytest.raises(ValueError, match="Geçersiz kampanya geçişi"):
        kd.gecis_yap(mevcut, hedef)
    assert kd.gecis_izinli_mi(mevcut, hedef) is False


@pytest.mark.parametrize("uc", sorted(kd.UC_DURUMLAR))
def test_uc_durumdan_cikis_yok(uc: str) -> None:
    assert kd.izinli_gecisler(uc) == ()
    assert kd.uc_durum_mu(uc) is True
    with pytest.raises(ValueError, match="uç durumdur"):
        kd.gecis_yap(uc, "aktif")


# --- bilinmeyen / bozuk girdi ---------------------------------------------
@pytest.mark.parametrize("bozuk", ["", "yok", "active", "TASLAK ", None, 42])
def test_bilinmeyen_durum_valueerror(bozuk) -> None:  # noqa: ANN001
    if bozuk == "TASLAK ":
        # normalize edilir: kırp + küçük harf → geçerli
        assert kd.durum_dogrula(bozuk) == "taslak"
        return
    with pytest.raises(ValueError):
        kd.durum_dogrula(bozuk)
    with pytest.raises(ValueError):
        kd.gecis_yap(bozuk, "aktif")
    with pytest.raises(ValueError):
        kd.gecis_yap("taslak", bozuk)


# --- izinli_gecisler tablosu ---------------------------------------------
def test_izinli_gecisler_tam_tablo_tum_durumlari_kapsar() -> None:
    tablo = kd.izinli_gecisler()
    assert isinstance(tablo, dict)
    assert tuple(tablo) == kd.DURUMLAR
    beklenen = {(m, h) for m, hs in tablo.items() for h in hs}
    assert beklenen == IZINLI_SET


@pytest.mark.parametrize("durum", kd.DURUMLAR)
def test_izinli_gecisler_tekil_durum_sirali(durum: str) -> None:
    hedefler = kd.izinli_gecisler(durum)
    assert isinstance(hedefler, tuple)
    assert list(hedefler) == sorted(hedefler, key=kd.DURUMLAR.index)
    assert set(hedefler) == {h for m, h in IZINLI if m == durum}


def test_baslangic_durumu_taslak_ve_uc_degil() -> None:
    assert kd.BASLANGIC_DURUMU == "taslak"
    assert kd.uc_durum_mu(kd.BASLANGIC_DURUMU) is False


# --- tam yaşam döngüsü ---------------------------------------------------
def test_tam_yasam_dongusu_duraklat_devam_tamamla() -> None:
    d = kd.BASLANGIC_DURUMU
    for hedef in ("planlandı", "aktif", "duraklatıldı", "aktif", "tamamlandı"):
        d = kd.gecis_yap(d, hedef)
    assert d == "tamamlandı"
    assert kd.uc_durum_mu(d)


# --- DB eşlemesi (pazarlama.py status sütunu) -----------------------------
@pytest.mark.parametrize(("tr", "db"), [
    ("taslak", "draft"), ("planlandı", "scheduled"), ("aktif", "active"),
    ("duraklatıldı", "paused"), ("tamamlandı", "completed"), ("iptal", "cancelled"),
])
def test_db_esleme_cift_yonlu(tr: str, db: str) -> None:
    assert kd.db_deger(tr) == db
    assert kd.db_degerden(db) == tr
    assert kd.db_degerden(db.upper()) == tr  # normalize


def test_db_degerden_bilinmeyen_valueerror() -> None:
    with pytest.raises(ValueError, match="Bilinmeyen DB durumu"):
        kd.db_degerden("archived")


def test_pazarlama_aktif_degeri_ile_uyumlu() -> None:
    """pazarlama.ozet_rapor 'active' filtreler; eşleme bunu korumalı."""
    assert kd.db_deger(kd.AKTIF) == "active"
