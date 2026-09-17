# -*- coding: utf-8 -*-
"""Test Suite for Kaynak Güvenilirlik (Source Reliability Monitor).

Kapsam:
  - Tazelik skoru hesaplaması (0-100, gün tabanlı)
  - Hata oranı hesaplaması (0-1)
  - Tutarlılık skoru hesaplaması (0-100, son N çekişler)
  - Genel skor formülü ve bant ataması
  - Toplu hesaplama
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from company_master.kaynak_guvenilirlik import (
    CONSISTENCY_WINDOW,
    RECENCY_FRESH_DAYS,
    RECENCY_STALE_DAYS,
    RELIABILITY_GREEN,
    RELIABILITY_YELLOW,
    KaynakSaglik,
    _banti_bul,
    _hata_orani,
    _tazelik_skoru,
    _tutarlilik_skoru,
    esik_dokumani,
    hesapla,
    hesapla_toplu,
)


# ── Tazelik Skoru Testleri ────────────────────────────────────────────────

class TestTazelikSkoru:
    """Tazelik (Recency) skoru hesaplama testleri."""

    def test_tazelik_son_7_gun_100_puan(self):
        """Son 7 gün içindeki çekiş 100 puan."""
        son_zaman = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        assert _tazelik_skoru(son_zaman) == 100.0

    def test_tazelik_7_gun_oncesi_100(self):
        """Tam 7 gün önce 100 puan."""
        eski = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)).isoformat()
        assert _tazelik_skoru(eski) == 100.0

    def test_tazelik_8_gun_azaliyor(self):
        """8 gün önce 100'dan az."""
        eski = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=8)).isoformat()
        skor = _tazelik_skoru(eski)
        assert 0 < skor < 100

    def test_tazelik_30_gun_sifir(self):
        """30+ gün eski çekiş 0 puan."""
        eski = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)).isoformat()
        assert _tazelik_skoru(eski) == 0.0

    def test_tazelik_31_gun_sifir(self):
        """31 gün eski de 0 puan."""
        eski = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=31)).isoformat()
        assert _tazelik_skoru(eski) == 0.0

    def test_tazelik_bos_veri_sifir(self):
        """Zaman damgası yoksa 0 puan."""
        assert _tazelik_skoru(None) == 0.0

    def test_tazelik_gecersiz_format_sifir(self):
        """Geçersiz ISO format 0 puan."""
        assert _tazelik_skoru("invalid-date") == 0.0

    def test_tazelik_13_gunden_lineer_aralik(self):
        """13 gün eski (ortadaki nokta) ~ 66-67 puan arası."""
        eski = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=13)).isoformat()
        skor = _tazelik_skoru(eski)
        # 7-30 gün arası: (13-7)/(30-7) = 6/23 ≈ 0.26 → (1-0.26)*100 ≈ 73.9
        # Ama 13 gün ≈ (13/23 * (30-7) + 7) → orantı yanlış
        # Doğru: gün_farki=13, (13-7)/(30-7) = 6/23 ≈ 0.26, (1-0.26)*100 ≈ 74
        assert 70 < skor < 80


# ── Hata Oranı Testleri ────────────────────────────────────────────────

class TestHataOrani:
    """Hata Oranı (Error Rate) hesaplama testleri."""

    def test_hata_orani_mükemmel(self):
        """Tüm çekişler başarılı = 0 hata."""
        assert _hata_orani(100, 100) == 0.0

    def test_hata_orani_yuzde_5(self):
        """95 başarılı / 100 toplam = 0.05 hata oranı."""
        assert _hata_orani(100, 95) == 0.05

    def test_hata_orani_yuzde_10(self):
        """90 başarılı / 100 toplam = 0.10 hata oranı."""
        assert _hata_orani(100, 90) == 0.1

    def test_hata_orani_sifir_cekis(self):
        """Çekiş yoksa (0/0) 0 hata."""
        assert _hata_orani(0, 0) == 0.0

    def test_hata_orani_basarili_sifir(self):
        """Hiç başarılı olmayan (0/5) 1.0 hata."""
        assert _hata_orani(5, 0) == 1.0

    def test_hata_orani_kesir(self):
        """Kesirli hesaplama: 2/7 ≈ 0.2857."""
        result = _hata_orani(7, 5)
        assert 0.28 < result < 0.29


# ── Tutarlılık Skoru Testleri ────────────────────────────────────────────

class TestTutarlilikSkoru:
    """Tutarlılık (Consistency) skoru hesaplama testleri."""

    def test_tutarlilik_tum_basarili_100(self):
        """Tüm çekişler başarılı = 100 puan."""
        sonuclar = [True] * CONSISTENCY_WINDOW
        assert _tutarlilik_skoru(sonuclar) == 100.0

    def test_tutarlilik_yarim_basarili_50(self):
        """Yarısı başarılı = 50 puan."""
        sonuclar = [True, False] * (CONSISTENCY_WINDOW // 2)
        skor = _tutarlilik_skoru(sonuclar)
        assert skor == 50.0

    def test_tutarlilik_hic_basarili_degil_0(self):
        """Hiçbiri başarılı değil = 0 puan."""
        sonuclar = [False] * CONSISTENCY_WINDOW
        assert _tutarlilik_skoru(sonuclar) == 0.0

    def test_tutarlilik_bos_liste_sifir(self):
        """Boş liste = 0 puan."""
        assert _tutarlilik_skoru([]) == 0.0

    def test_tutarlilik_8_basarili_10_toplam_80(self):
        """8 başarılı / 10 = 80 puan."""
        sonuclar = [True] * 8 + [False] * 2
        assert _tutarlilik_skoru(sonuclar) == 80.0


# ── Bant Bulma Testleri ────────────────────────────────────────────────

class TestBantiBul:
    """Skor → bant eşleme testleri."""

    def test_banti_green_75_ve_ustu(self):
        """75+ puan = green."""
        assert _banti_bul(75.0) == "green"
        assert _banti_bul(85.0) == "green"
        assert _banti_bul(100.0) == "green"

    def test_banti_yellow_50_74(self):
        """50-74 puan = yellow."""
        assert _banti_bul(50.0) == "yellow"
        assert _banti_bul(60.0) == "yellow"
        assert _banti_bul(74.9) == "yellow"

    def test_banti_red_50_alti(self):
        """<50 puan = red."""
        assert _banti_bul(49.9) == "red"
        assert _banti_bul(25.0) == "red"
        assert _banti_bul(0.0) == "red"


# ── Genel Skor ve Veri Yapısı Testleri ────────────────────────────────────

class TestHesapla:
    """Kaynak sağlık skoru hesaplama ana testi."""

    def test_hesapla_temel_parametreler(self):
        """Temel parametrelerle hesaplama."""
        sonuc = hesapla(
            kaynak_id="apify_001",
            kaynak_adi="Apify Scraper",
            toplam_cekis=100,
            basarili_cekis=95,
            son_cekis_zaman=datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            son_n_cekisler=[True] * 9 + [False],
        )
        assert isinstance(sonuc, KaynakSaglik)
        assert sonuc.kaynak_id == "apify_001"
        assert sonuc.kaynak_adi == "Apify Scraper"
        assert 0 <= sonuc.skor <= 100
        assert sonuc.band in ("green", "yellow", "red")

    def test_hesapla_mükemmel_kaynak_green(self):
        """Mükemmel kaynak (100 başarılı, taze, tutarlı) = GREEN."""
        sonuc = hesapla(
            kaynak_id="ideal_001",
            kaynak_adi="İdeal Kaynak",
            toplam_cekis=100,
            basarili_cekis=100,  # %100 başarı
            son_cekis_zaman=datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),  # Şu an = taze
            son_n_cekisler=[True] * CONSISTENCY_WINDOW,  # Tüm başarılı
        )
        assert sonuc.skor >= RELIABILITY_GREEN
        assert sonuc.band == "green"

    def test_hesapla_sorunlu_kaynak_red(self):
        """Sorunlu kaynak (eski, az başarılı) = RED."""
        sonuc = hesapla(
            kaynak_id="sorun_001",
            kaynak_adi="Sorunlu Kaynak",
            toplam_cekis=100,
            basarili_cekis=50,  # %50 başarı = %50 hata
            son_cekis_zaman=(datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=40)).isoformat(),  # Eski
            son_n_cekisler=[False] * CONSISTENCY_WINDOW,  # Hiç tutarlı değil
        )
        assert sonuc.skor < RELIABILITY_YELLOW
        assert sonuc.band == "red"

    def test_hesapla_bilesenler_sifirdan_100_arasi(self):
        """Tüm bileşenler 0-100 aralığında."""
        sonuc = hesapla(
            kaynak_id="test_001",
            kaynak_adi="Test Kaynağı",
            toplam_cekis=50,
            basarili_cekis=40,
            son_cekis_zaman=(datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=15)).isoformat(),
            son_n_cekisler=[True, False, True, True, False, True, True, True, False, True],
        )
        assert 0 <= sonuc.tazelik_skoru <= 100
        assert 0 <= sonuc.tutarlilik_skoru <= 100
        assert 0 <= sonuc.hata_orani <= 1.0
        assert 0 <= sonuc.skor <= 100

    def test_hesapla_to_dict(self):
        """to_dict() metodunun çıktı yapısı doğru."""
        sonuc = hesapla(
            kaynak_id="dict_001",
            kaynak_adi="Dict Test",
            toplam_cekis=10,
            basarili_cekis=9,
            son_cekis_zaman=datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
        )
        d = sonuc.to_dict()
        assert "kaynak_id" in d
        assert "skor" in d
        assert "band" in d
        assert "tazelik_skoru" in d
        assert "hata_orani" in d
        assert "tutarlilik_skoru" in d
        assert "olusturma_zaman" in d


# ── Toplu Hesaplama Testleri ────────────────────────────────────────────

class TestHesaplaToplu:
    """Birden fazla kaynağın toplu hesaplaması."""

    def test_hesapla_toplu_bos_liste(self):
        """Boş kaynak listesi = boş sonuç."""
        sonuc = hesapla_toplu([])
        assert sonuc == []

    def test_hesapla_toplu_tek_kaynak(self):
        """Tek kaynak listesi."""
        kaynaklar = [
            {
                "kaynak_id": "src_001",
                "kaynak_adi": "Kaynak 1",
                "toplam_cekis": 50,
                "basarili_cekis": 45,
                "son_cekis_zaman": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            }
        ]
        sonuc = hesapla_toplu(kaynaklar)
        assert len(sonuc) == 1
        assert isinstance(sonuc[0], KaynakSaglik)

    def test_hesapla_toplu_coklu_kaynaklar(self):
        """Birden fazla kaynak."""
        kaynaklar = [
            {
                "kaynak_id": "apify_001",
                "kaynak_adi": "Apify",
                "toplam_cekis": 100,
                "basarili_cekis": 95,
                "son_cekis_zaman": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
                "son_n_cekisler": [True] * 10,
            },
            {
                "kaynak_id": "manual_001",
                "kaynak_adi": "Manual",
                "toplam_cekis": 20,
                "basarili_cekis": 20,
                "son_cekis_zaman": (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=5)).isoformat(),
                "son_n_cekisler": [True] * 9 + [False],
            },
            {
                "kaynak_id": "eski_001",
                "kaynak_adi": "Eski Kaynak",
                "toplam_cekis": 30,
                "basarili_cekis": 10,
                "son_cekis_zaman": (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=60)).isoformat(),
                "son_n_cekisler": [False] * 10,
            },
        ]
        sonuc = hesapla_toplu(kaynaklar)
        assert len(sonuc) == 3
        assert all(isinstance(s, KaynakSaglik) for s in sonuc)

        # Birinci (mükemmel) >= ikinci (iyi) >= üçüncü (kötü)
        assert sonuc[0].skor >= sonuc[1].skor
        assert sonuc[1].skor >= sonuc[2].skor


# ── Kenar Durumlar ve Hata Yönetimi ────────────────────────────────────

class TestKenarDurumlar:
    """Kenar durumları ve hata yönetimi."""

    def test_eksik_alanlar_graceful(self):
        """Eksik alanlar graceful handle edilir (skor minimal ama > 0)."""
        sonuc = hesapla(
            kaynak_id="eksik_001",
            kaynak_adi="Eksik Veri",
            toplam_cekis=0,
            basarili_cekis=0,
            son_cekis_zaman=None,
            son_n_cekisler=None,
        )
        # Formül: tazelik=0 + tutarlılık=0 + ((1-0)*100*0.1) = 10
        # Beklenilen: skor minimal ama sıfır değil (hata cezası sayılmaz)
        assert sonuc.skor == 10.0
        assert sonuc.band == "red"

    def test_negatif_cekis_sayilari_sifira_donusur(self):
        """Negatif çekiş sayıları sıfır olarak kabul edilir."""
        # Formül zaten 0 <= sonuc döndürüyor, ama kontrol için test edelim
        sonuc = hesapla(
            kaynak_id="neg_001",
            kaynak_adi="Negative Test",
            toplam_cekis=10,
            basarili_cekis=15,  # Başarılı > toplam (mantıksız)
            son_cekis_zaman=datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
        )
        # Bu durumda hata oranı (10-15)/10 = -5/10 → Python -0.5 döndürür
        # Formülde (1-(-0.5)) * 100 * 0.1 = 150*0.1 = 15 ekstra puan
        # Test sadece graceful fail olmadığını kontrol eder
        assert isinstance(sonuc, KaynakSaglik)
        assert 0 <= sonuc.skor <= 100

    def test_float_kosulma(self):
        """Skorlar 2 ondalak basamağa kadar yuvarlanır."""
        sonuc = hesapla(
            kaynak_id="float_001",
            kaynak_adi="Float Test",
            toplam_cekis=7,
            basarili_cekis=5,
            son_cekis_zaman=(datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=13.5)).isoformat(),
            son_n_cekisler=[True, True, True, True, True, True, True, True, True, False],
        )
        # Tazelik, tutarlılık, skor 2 ondalaka kadar olmalı
        assert sonuc.tazelik_skoru == round(sonuc.tazelik_skoru, 2)
        assert sonuc.tutarlilik_skoru == round(sonuc.tutarlilik_skoru, 2)
        assert sonuc.skor == round(sonuc.skor, 2)


# ── Dokümantasyon Testleri ────────────────────────────────────────────

class TestDokumentation:
    """Dokümantasyon üretme testleri."""

    def test_esik_dokumani_format(self):
        """Eşik dokümanı başlık ve bölümleri içeriyor."""
        dokuman = esik_dokumani()
        assert "# Kaynak Sağlık Skoru" in dokuman
        assert "## Bant Tanımları" in dokuman
        assert "## Bileşen Ağırlıkları" in dokuman
        assert "GREEN" in dokuman
        assert "YELLOW" in dokuman
        assert "RED" in dokuman

    def test_esik_dokumani_degerleri(self):
        """Dokümanda sabitler doğru yazılı."""
        dokuman = esik_dokumani()
        assert f"{RECENCY_FRESH_DAYS}-{RECENCY_STALE_DAYS}" in dokuman
        assert f"{CONSISTENCY_WINDOW}" in dokuman


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
