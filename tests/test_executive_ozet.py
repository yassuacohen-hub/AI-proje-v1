# -*- coding: utf-8 -*-
"""PO-BACK-08: Executive özet (MRR/ARR · churn · tenant sağlık dağılımı) testleri.

Kapsam: `src/company_master/executive_ozet.py` saf fonksiyonları. Streamlit ve
veritabanı **gerekmez**; tüm girdiler sözlük olarak enjekte edilir.

Sözleşmeler (testle kilitlenen davranışlar):
  - Ücret kaynağı: kayıttaki açık ücret → paket adından ``fiyat_katalogu()``.
  - Bant kaynağı: ``band`` alanı → skordan ``health.py`` eşikleriyle hesap.
  - Bozuk/eksik girdi hata fırlatmaz; 0 ya da boş dağılım döner.
"""
from __future__ import annotations

import pytest

from company_master.executive_ozet import (
    BANTLAR,
    abonelik_aktif_mi,
    abonelik_ucreti,
    churn_orani,
    health_dagilimi,
    mrr_arr,
    mrr_trend,
    paket_fiyatlari,
)
from company_master.paketler import fiyat_katalogu
from company_master.tenant.health import HEALTH_GREEN, HEALTH_YELLOW, hesapla
from company_master.tenant.model import TenantContext, VARSAYILAN_TENANT


# ---------------------------------------------------------------------------
# Fiyat kaynağı (tek kaynak: paketler.fiyat_katalogu)
# ---------------------------------------------------------------------------


def test_paket_fiyatlari_tek_kaynaktan_turetilir():
    """Modül kendi fiyat tablosunu tutmaz; katalogla birebir aynı olmalı."""
    katalog = {p["name"]: float(p["price"]) for p in fiyat_katalogu()}
    assert paket_fiyatlari() == katalog
    assert paket_fiyatlari()["Kurumsal"] == 19999.0


def test_abonelik_ucreti_acik_ucret_paket_fiyatini_ezer():
    kayit = {"paket": "Temel", "aylik_ucret": 123.45}
    assert abonelik_ucreti(kayit) == pytest.approx(123.45)


@pytest.mark.parametrize(
    "paket, beklenen",
    [("Temel", 499.0), ("Standart", 2999.0), ("Profesyonel", 7999.0), ("Kurumsal", 19999.0)],
)
def test_abonelik_ucreti_paket_adindan_turetilir(paket, beklenen):
    assert abonelik_ucreti({"paket": paket}) == pytest.approx(beklenen)


def test_abonelik_ucreti_bilinmeyen_paket_sifir():
    """Bilinmeyen/boş paket sessizce 0 sayılır (ekran düşmez)."""
    assert abonelik_ucreti({"paket": "Yok Böyle Paket"}) == 0.0
    assert abonelik_ucreti({"paket": "Temel", "aylik_ucret": "abc"}) == 0.0
    assert abonelik_ucreti({"aylik_ucret": "2.999,50"}) == pytest.approx(2999.5)


# ---------------------------------------------------------------------------
# Aktiflik kuralı
# ---------------------------------------------------------------------------


def test_abonelik_aktif_mi_iptal_ve_gecmis_bitis():
    assert abonelik_aktif_mi({"paket": "Temel", "durum": "aktif"}) is True
    assert abonelik_aktif_mi({"paket": "Temel", "durum": "iptal"}) is False
    assert abonelik_aktif_mi({"paket": "Temel", "durum": "aktif", "bitis": "2020-01-01"}) is False
    # Durum bilinmiyorsa ve bitiş yoksa yürürlükte varsayılır (eksik alan cezalandırılmaz)
    assert abonelik_aktif_mi({"paket": "Temel"}) is True


# ---------------------------------------------------------------------------
# mrr_arr
# ---------------------------------------------------------------------------


def test_mrr_arr_bos_ve_none_girdi():
    for girdi in (None, [], "bozuk"):
        sonuc = mrr_arr(girdi)  # type: ignore[arg-type]
        assert sonuc["mrr"] == 0.0
        assert sonuc["arr"] == 0.0
        assert sonuc["arpa"] == 0.0
        assert sonuc["aktif_abonelik"] == 0


def test_mrr_arr_aktif_aboneliklerden_toplam_ve_arr():
    kayitlar = [
        {"paket": "Temel", "durum": "aktif"},
        {"paket": "Profesyonel", "durum": "aktif"},
    ]
    sonuc = mrr_arr(kayitlar)
    assert sonuc["mrr"] == pytest.approx(499.0 + 7999.0)
    assert sonuc["arr"] == pytest.approx((499.0 + 7999.0) * 12)
    assert sonuc["arpa"] == pytest.approx((499.0 + 7999.0) / 2)
    assert sonuc["aktif_abonelik"] == 2


def test_mrr_arr_pasif_abonelikleri_saymaz():
    kayitlar = [
        {"paket": "Kurumsal", "durum": "aktif"},
        {"paket": "Kurumsal", "durum": "iptal"},
        {"paket": "Temel", "durum": "aktif", "bitis": "2020-01-01"},
    ]
    sonuc = mrr_arr(kayitlar)
    assert sonuc["mrr"] == pytest.approx(19999.0)
    assert sonuc["aktif_abonelik"] == 1
    assert sonuc["pasif_abonelik"] == 2
    assert sonuc["toplam_abonelik"] == 3


def test_mrr_arr_paket_dagilimi_ve_bozuk_kayit_atlama():
    kayitlar = [
        {"paket": "Temel", "durum": "aktif"},
        {"paket": "Temel", "durum": "aktif"},
        {"paket": "Kurumsal", "durum": "aktif"},
        "metin-degil-sozluk",
        None,
    ]
    sonuc = mrr_arr(kayitlar)  # type: ignore[list-item]
    assert sonuc["paket_dagilimi"] == {"Temel": 2, "Kurumsal": 1}
    # Bozuk kayıtlar toplama girmez; yalnızca aktif sözlükler sayılır
    assert sonuc["aktif_abonelik"] == 3
    assert sonuc["mrr"] == pytest.approx(499.0 * 2 + 19999.0)


# ---------------------------------------------------------------------------
# churn_orani
# ---------------------------------------------------------------------------


def test_churn_orani_yarisi_donem_icinde_iptal():
    kayitlar = [
        {"paket": "Temel", "baslangic": "2025-01-01"},
        {"paket": "Temel", "baslangic": "2025-01-01", "bitis": "2026-02-10"},
    ]
    assert churn_orani("2026-01-01", "2026-03-31", kayitlar) == pytest.approx(50.0)


def test_churn_orani_payda_bos_ise_sifir():
    kayitlar = [{"paket": "Temel", "baslangic": "2026-06-01"}]
    assert churn_orani("2026-01-01", "2026-03-31", kayitlar) == 0.0
    assert churn_orani("2026-01-01", "2026-03-31", None) == 0.0
    assert churn_orani("2026-01-01", "2026-03-31") == 0.0


@pytest.mark.parametrize(
    "baslangic, bitis",
    [(None, None), ("", ""), ("2026-03-31", "2026-01-01"), ("bozuk", "2026-01-01")],
)
def test_churn_orani_gecersiz_donem_sifir(baslangic, bitis):
    kayitlar = [{"paket": "Temel", "baslangic": "2025-01-01", "bitis": "2026-02-10"}]
    assert churn_orani(baslangic, bitis, kayitlar) == 0.0


def test_churn_orani_donem_disindaki_iptaller_sayilmaz():
    kayitlar = [
        {"paket": "Temel", "baslangic": "2025-01-01", "bitis": "2025-12-31"},
        {"paket": "Temel", "baslangic": "2025-01-01", "bitis": "2026-06-30"},
    ]
    # Dönem 2026 Q1: yalnız ikinci kayıt dönem başında yürürlükteydi, iptali dönem dışı
    assert churn_orani("2026-01-01", "2026-03-31", kayitlar) == 0.0


def test_churn_orani_tr_tarih_bicimini_kabul_eder():
    kayitlar = [
        {"paket": "Temel", "baslangic": "01.01.2025"},
        {"paket": "Temel", "baslangic": "01.01.2025", "bitis": "10.02.2026"},
    ]
    assert churn_orani("01.01.2026", "31.03.2026", kayitlar) == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# health_dagilimi
# ---------------------------------------------------------------------------


def test_bantlar_ve_esikler_health_moduluyle_ayni():
    """Bant sözlüğü health.py ile hizalı; eşikler oradan okunur."""
    assert set(BANTLAR) == {"green", "yellow", "red"}
    assert HEALTH_GREEN == 85.0 and HEALTH_YELLOW == 60.0


def test_health_dagilimi_bant_alanindan_okur():
    dagilim = health_dagilimi([{"band": "green"}, {"band": "yellow"}, {"band": "GREEN"}])
    assert dagilim == {"green": 2, "yellow": 1, "red": 0}


@pytest.mark.parametrize(
    "skor, beklenen",
    [(100, "green"), (85, "green"), (84.99, "yellow"), (60, "yellow"), (59.99, "red"), (0, "red")],
)
def test_health_dagilimi_skordan_bant_hesaplar(skor, beklenen):
    dagilim = health_dagilimi([{"overall_score": skor}])
    assert dagilim[beklenen] == 1
    assert sum(dagilim.values()) == 1


def test_health_dagilimi_bos_girdi_uc_anahtar_dondurur():
    for girdi in (None, [], "bozuk"):
        dagilim = health_dagilimi(girdi)  # type: ignore[arg-type]
        assert dagilim == {"green": 0, "yellow": 0, "red": 0}


def test_health_dagilimi_bilinmeyen_kayit_sayilmaz():
    dagilim = health_dagilimi([None, {}, {"band": "mavi"}, {"overall_score": "abc"}, 42])
    assert dagilim == {"green": 0, "yellow": 0, "red": 0}
    assert sum(dagilim.values()) == 0


def test_health_dagilimi_gercek_tenant_skorunu_tuketir():
    """health.hesapla() çıktısı (TenantHealthScore) doğrudan tüketilebilir."""
    skor = hesapla(
        TenantContext("huginn", "Huginn Data", "kurumsal"),
        [{"data_quality_score": 95, "nace_code": "6201", "adres": "Ankara"}],
    )
    dagilim = health_dagilimi([skor])
    assert sum(dagilim.values()) == 1
    assert dagilim[skor.band] == 1
    # to_dict() çıktısı da aynı sonucu vermeli (UI bu biçimi kullanır)
    assert health_dagilimi([skor.to_dict()])[skor.band] == 1


def test_health_dagilimi_varsayilan_tenant_skoru():
    skor = hesapla(VARSAYILAN_TENANT, [])
    dagilim = health_dagilimi([skor])
    assert sum(dagilim.values()) == 1


# ---------------------------------------------------------------------------
# mrr_trend
# ---------------------------------------------------------------------------


def test_mrr_trend_ay_sayisi_siralama_ve_etiket():
    kayitlar = [
        {"paket": "Temel", "baslangic": "2025-01-01"},
        {"paket": "Standart", "baslangic": "2026-08-01"},
    ]
    seri = mrr_trend(kayitlar, 3, "2026-09-15")
    assert [satir["ay"] for satir in seri] == ["2026-07", "2026-08", "2026-09"]
    assert seri[0]["mrr"] == pytest.approx(499.0)
    assert seri[1]["mrr"] == pytest.approx(499.0 + 2999.0)
    assert seri[2]["aktif_abonelik"] == 2


def test_mrr_trend_iptal_edilen_abonelik_sonraki_aylarda_dusmez():
    kayitlar = [
        {"paket": "Temel", "baslangic": "2025-01-01"},
        {"paket": "Kurumsal", "baslangic": "2025-01-01", "bitis": "2026-08-15"},
    ]
    seri = mrr_trend(kayitlar, 3, "2026-09-15")
    assert seri[0]["mrr"] == pytest.approx(499.0 + 19999.0)
    assert seri[1]["mrr"] == pytest.approx(499.0 + 19999.0)
    assert seri[2]["mrr"] == pytest.approx(499.0)
    assert seri[2]["aktif_abonelik"] == 1


def test_mrr_trend_gecersiz_ay_sayisi_bos_liste():
    kayitlar = [{"paket": "Temel", "baslangic": "2025-01-01"}]
    assert mrr_trend(kayitlar, 0, "2026-09-15") == []
    assert mrr_trend(kayitlar, -3, "2026-09-15") == []
    assert mrr_trend(kayitlar, "abc", "2026-09-15") == []


def test_mrr_trend_bos_girdi_varsayilan_alti_ay_sifir():
    seri = mrr_trend(None, referans="2026-09-15")  # type: ignore[arg-type]
    assert len(seri) == 6
    assert all(satir["mrr"] == 0.0 and satir["aktif_abonelik"] == 0 for satir in seri)

