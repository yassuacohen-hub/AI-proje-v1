"""D-285 OSTIM birlestirme kalite testleri (regresyon sabiti).

Bu testler, `birlestirme_kalite_kontrol.py` ile OLULEN 3 kirligi
KALICI olarak korur. Amac: filtreler ileride biri tarafindan
kaldirilirsa test KIRMIZI olsun.

Kapsam:
  1. OSTIM'in kendi sosyal hesaplari firmaya tasinmaz
  2. Ortak altyapi siteleri (isim.org.tr, ostimistihdam.com) tasinmaz
  3. "Adres bilgisi girilmemistir" dolgu metni adres sayilmaz
  4. Gercek firma verisi KORUNUR (filtre fazla genis olmamali)

Kullanim: python -m pytest tests/test_ostim_birlestirme_kalite.py -v
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

KOK = pathlib.Path(__file__).resolve().parents[1]
SP = KOK / "scripts" / "ostim_set_birlestir.py"


def _mod():
    spec = importlib.util.spec_from_file_location("ostim_birlestir", SP)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def b():
    return _mod()


# --- 1. SOSYAL MEDYA KIRLIGI (5.000 kayit) -------------------------

def test_site_hesabi_sosyal_medyaya_girmez(b):
    kirli = {
        "facebook": "https://www.facebook.com/OstimOSB",
        "instagram": "https://www.instagram.com/ostim_osb/",
        "twitter": "https://x.com/ostimosb",
        "linkedin": "https://www.linkedin.com/company/ostim-osb/",
    }
    assert b._deger_guvenli_mi("sosyal_medya", kirli) is False


def test_sitenin_kendisine_ait_domain_engellenir(b):
    assert b._deger_guvenli_mi(
        "web_sitesi", "http://www.ostim.org.tr") is False


# --- 2. ORTAK ALTYAPI SITELERI -----------------------------------

@pytest.mark.parametrize("kirli", [
    "http://www.isim.org.tr", "https://www.isim.org.tr",
    "https://www.ostimistihdam.com", "http://www.htk.org.tr",
])
def test_altyapi_sitesi_reddedilir(b, kirli):
    """isim.org.tr 2.155, ostimistihdam.com 475, htk.org.tr 2 kayit."""
    assert b._deger_guvenli_mi("web_sitesi", kirli) is False


# --- 3. DOLGU METNI ------------------------------------------------

@pytest.mark.parametrize("dolgu", [
    "Adres bilgisi girilmemis",
    "Adres bilgisi girilmemistir",
    "bilgi yok",
    "belirtilmemis",
])
def test_dolgu_metni_gercek_veri_sayilmaz(b, dolgu):
    assert b._deger_guvenli_mi("adres", dolgu) is False


def test_tire_ve_na_yalnizca_adres_alani(b):
    """D-285 regresyon: `-` her alanda gecerli degildir.

    Onceki surum `_DOLGU_METIN` icinde `-` oldugu icin URL'li her
    sosyal medya hesabini ve her telefonu reddediyordu.
    """
    assert b._deger_guvenli_mi("adres", "-") is False
    # ama web/telefon kirp degil
    assert b._deger_guvenli_mi(
        "web_sitesi", "http://www.senkronplastik.com") is True
    assert b._deger_guvenli_mi("telefonler", "0312 397 80 00") is True


# --- 4. GERCEK FIRMA VERISI KORUNMALI (asiri filtre tuzagi) ------

@pytest.mark.parametrize("iyi", [
    "http://www.senkronplastik.com",
    "https://guveniskele.com",
    "http://ziyacomertogludamper.com",
])
def test_gercek_firma_sitesi_korunur(b, iyi):
    assert b._deger_guvenli_mi("web_sitesi", iyi) is True


def test_gercek_sosyal_medya_korunur(b):
    gercek = {
        "facebook": "https://www.facebook.com/senkronplastik",
        "linkedin": "https://www.linkedin.com/company/senkron-plastik/",
    }
    assert b._deger_guvenli_mi("sosyal_medya", gercek) is True


def test_gercek_adres_korunur(b):
    assert b._deger_guvenli_mi(
        "adres", "100. YIL BULVARI 55E 14") is True


def test_gercek_telefon_korunur(b):
    assert b._deger_guvenli_mi("telefonler", "+90 312 397 80 00") is True


# --- 5. BOS DEGER REDDI --------------------------------------------

def test_bos_deger_guvenli_degil(b):
    assert b._deger_guvenli_mi("adres", None) is False
    assert b._deger_guvenli_mi("adres", "") is False
    assert b._deger_guvenli_mi("sosyal_medya", {}) is False
