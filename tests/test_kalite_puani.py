# -*- coding: utf-8 -*-
"""D-250 mandallari: kimlik tamligi (0-10) TEK KAPIDAN gecer.

Cerceve yok, assert yeter. pre-commit kancasindan gecer.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from company_master.etl import normalize  # noqa: E402
from company_master.etl.quality_recalc import (  # noqa: E402
    AGIRLIKLAR,
    SURUM,
    alan_puanlari,
    bayat_mi,
    identity_completeness,
)

# Gercek olcum verisinden dogrulanmis VKN (kimlik_no.py mandallariyla ayni).
VKN = "3102014174"
MERSIS = VKN + "012345"

TAM = {
    "legal_name": "ORNEK SAN. VE TIC. A.S.",
    "tax_number": VKN,
    "tax_office": "OSTIM",
    "mersis_number": MERSIS,
    "trade_registry_number": "123456",
    "trade_registry_office": "ANKARA",
    "nace_code": "25.11",
    "nace_source": "mersis",
    "address": "Ostim Mah. 1. Cad. No:1",
    "primary_phone": "03123120000",
    "primary_email": "a@b.com",
    "website_domain": "b.com",
}


def test_agirlik_toplami_tam_10():
    """Kayan nokta toplamina dikkat: 1.5+0.7+0.3 gibi terimler var."""
    t = round(sum(AGIRLIKLAR.values()), 10)
    assert t == 10.0, f"agirlik toplami 10.0 degil: {t!r}"


def test_kimlik_omurgasi_6_erisim_4():
    omurga = ("legal_name", "tax_number", "tax_office", "mersis_number",
              "trade_registry_number", "nace_code")
    erisim = ("address", "primary_phone", "primary_email", "website_domain")
    assert set(omurga) | set(erisim) == set(AGIRLIKLAR), "agirlik seti eksik/fazla"
    assert round(sum(AGIRLIKLAR[k] for k in omurga), 10) == 6.0
    assert round(sum(AGIRLIKLAR[k] for k in erisim), 10) == 4.0


def test_tam_satir_10_bos_satir_0():
    assert identity_completeness(TAM) == 10.0
    assert identity_completeness({}) == 0.0


def test_dogrulanmamis_deger_0_puan():
    """D-246: kapidan gecmeyen kimlik puan almaz."""
    assert alan_puanlari({"tax_number": "1234567890"})["tax_number"] == 0.0
    assert alan_puanlari({"tax_number": "1111111111"})["tax_number"] == 0.0
    assert alan_puanlari({"tax_number": "99999999999"})["tax_number"] == 0.0
    # Ilk 10 hane gecerli VKN degilse MERSIS de gecersizdir (kimlik_no mandali).
    assert alan_puanlari({"mersis_number": "1111111110012345"})["mersis_number"] == 0.0
    assert alan_puanlari({"mersis_number": "310201417401234"})["mersis_number"] == 0.0
    # Tam satirda bile sahte VKN puani sifirlar.
    assert alan_puanlari(dict(TAM, tax_number="1234567890"))["tax_number"] == 0.0
    assert identity_completeness(dict(TAM, tax_number="1234567890")) == 8.5


def test_tahmin_nace_puan_almaz():
    """D-245: deger var + kaynak yok = kabul edilmez."""
    for kaynak in ("sector_default", "unknown", "fallback", "title_default",
                   "predicted", "invalid_cleared", None):
        assert alan_puanlari({"nace_code": "25.11", "nace_source": kaynak})[
            "nace_code"] == 0.0, f"tahmin NACE puan aldi: {kaynak}"
    for kaynak in ("mersis", "external"):
        assert alan_puanlari({"nace_code": "25.11", "nace_source": kaynak})[
            "nace_code"] == 1.0


def test_sicil_no_tek_basina_yetmez():
    assert alan_puanlari({"trade_registry_number": "123456"})[
        "trade_registry_number"] == 0.0
    assert alan_puanlari({"trade_registry_number": "123456",
                          "trade_registry_office": "ANKARA"})[
        "trade_registry_number"] == 1.0


def test_bos_dize_dolu_sayilmaz():
    assert identity_completeness(
        {"legal_name": "   ", "address": "", "primary_phone": None}) == 0.0


def test_aralik_disina_cikilamaz():
    ornekler = [{}, TAM, dict(TAM, tax_number=None), {"legal_name": "A"},
                dict(TAM, address="x" * 5000, employee_count=9999)]
    for o in ornekler:
        s = identity_completeness(o)
        assert 0.0 <= s <= 10.0, f"aralik disi: {s}"


def test_surum_uyusmazsa_bayat():
    """D-250/4: baska agirlik setiyle hesaplanmis puan bayattir."""
    assert bayat_mi(None) is True
    assert bayat_mi("v0") is True
    assert bayat_mi("v2") is True
    assert bayat_mi(SURUM) is False


def test_zenginlik_verisi_puana_girmez():
    """D-250/5: calisan sayisi, ilan, sosyal medya, OSB parsel puana girmez."""
    assert identity_completeness(dict(
        TAM, employee_count=500, social_media_score=9, job_postings=12,
        osb_parcel="12/3")) == 10.0


def test_tek_kapi_normalize_kendi_formulunu_yazmaz():
    """D-250/1: puan ureten ikinci yol kalmadi."""
    assert not hasattr(normalize, "CRITICAL_FIELDS")
    assert not hasattr(normalize, "_data_quality_score"), \
        "normalize hala kendi puan yolunu tutuyor"
    assert normalize._identity_completeness.__module__.endswith("normalize")
    kaynak = {
        "legal_name": TAM["legal_name"], "raw_tax_number": VKN,
        "raw_phone": TAM["primary_phone"], "raw_email": TAM["primary_email"],
        "raw_website": TAM["website_domain"],
        "raw_payload": {"adres": TAM["address"]},
    }
    # NACE/MERSIS/sicil/vergi dairesi kaynakta yok -> tavan 10-1-1-1-0.5 = 6.5
    assert normalize._identity_completeness(kaynak) == 6.5


if __name__ == "__main__":
    for ad, fn in sorted(globals().items()):
        if ad.startswith("test_"):
            fn()
            print(f"  OK {ad}")
    print("D-250 mandallari gecti")
