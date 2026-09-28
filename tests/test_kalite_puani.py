"""D-250 mandallari: toplam kalite puani tek kapidan gecer."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from company_master.etl import normalize  # noqa: E402
from company_master.etl.quality_recalc import kalite_puani  # noqa: E402

# D-251/1: satir anahtarlari kolon adidir, Ingilizce. raw_payload anahtarlari
# (asagida) kaynagin sozlesmesidir, Turkce kalir.
TAM = {
    "tax_number": "1234567890", "address": "Ostim Mah. 1. Cadde No:1",
    "primary_phone": "03123120000", "primary_email": "a@b.com",
    "website_domain": "b.com", "nace_code": "25.11", "osb_parcel": "12/3",
    "trade_name": "ORNEK A.S.",
}


def test_tam_dolu_100():
    assert kalite_puani(TAM) == 100.0


def test_bos_sifir():
    assert kalite_puani({}) == 0.0


def test_agirliklar_toplami_100():
    toplam = 0.0
    for alan in TAM:
        toplam += kalite_puani({alan: TAM[alan]})
    assert toplam == 100.0, f"agirliklar 100 etmiyor: {toplam}"


def test_bos_dize_dolu_sayilmaz():
    assert kalite_puani({"address": "   ", "trade_name": ""}) == 0.0


def test_tek_kapi_normalize_ayni_puani_verir():
    """D-250/1: normalize.py artik kendi formulunu yazmiyor."""
    assert not hasattr(normalize, "CRITICAL_FIELDS")
    kaynak = {
        "raw_tax_number": TAM["tax_number"], "raw_phone": TAM["primary_phone"],
        "raw_email": TAM["primary_email"], "raw_website": TAM["website_domain"],
        "trade_name": TAM["trade_name"],
        "raw_payload": {"adres": TAM["address"], "nace_code": TAM["nace_code"],
                        "osb_parsel": TAM["osb_parcel"]},
    }
    assert normalize._data_quality_score(kaynak) == 100.0


def test_alt_skorlar_puana_girmez():
    """D-250/2: bos alt skorlar puani dusurmez."""
    alt = dict(TAM, employee_count_score=None, job_postings_score=None,
               social_media_score=0)
    assert kalite_puani(alt) == 100.0


if __name__ == "__main__":
    for ad, fn in sorted(globals().items()):
        if ad.startswith("test_"):
            fn()
            print(f"  OK {ad}")
    print("D-250 mandallari gecti")
