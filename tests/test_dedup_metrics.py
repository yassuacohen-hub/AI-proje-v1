# -*- coding: utf-8 -*-
"""Test: dedup_metrics — Duplicate Rate hesaplama (PO-BACK-09)."""

from __future__ import annotations

import pytest

from company_master.dedup_metrics import (
    DedupResult,
    mukerrer_orani,
    mukerrer_orani_legacy,
)


# ---------------------------------------------------------------------------
# mukerrer_orani
# ---------------------------------------------------------------------------

class TestMukerrerOrani:
    """Temel mukerrer_orani testleri."""

    def test_bos_liste(self):
        """Boş liste → hepsi sıfır."""
        sonuc = mukerrer_orani([])
        assert sonuc == {
            "toplam": 0,
            "benzersiz": 0,
            "mukerrer": 0,
            "oran": 0.0,
            "kaynak_bazli": {},
        }

    def test_tum_benzersiz(self):
        """Tüm kayıtlar benzersiz → mukerrer=0, oran=0."""
        kayitlar = [
            {"vkn": "1111111111", "kaynak": "ostim"},
            {"vkn": "2222222222", "kaynak": "ivedik"},
            {"vkn": "3333333333", "kaynak": "baskent"},
        ]
        sonuc = mukerrer_orani(kayitlar)
        assert sonuc["toplam"] == 3
        assert sonuc["benzersiz"] == 3
        assert sonuc["mukerrer"] == 0
        assert sonuc["oran"] == 0.0
        assert sonuc["kaynak_bazli"] == {"ostim": 1, "ivedik": 1, "baskent": 1}

    def test_tum_mukerrer(self):
        """Tüm kayıtlar aynı VKN → 1 benzersiz, 2 mukerrer."""
        kayitlar = [
            {"vkn": "1234567890", "kaynak": "ostim"},
            {"vkn": "1234567890", "kaynak": "ivedik"},
            {"vkn": "1234567890", "kaynak": "baskent"},
        ]
        sonuc = mukerrer_orani(kayitlar)
        assert sonuc["toplam"] == 3
        assert sonuc["benzersiz"] == 1
        assert sonuc["mukerrer"] == 2
        assert sonuc["oran"] == 0.6667  # 2/3 rounded to 4 decimal places

    def test_karisik(self):
        """Karışık: 2 benzersiz + 1 mukerrer (toplam 4)."""
        kayitlar = [
            {"vkn": "1111111111", "kaynak": "ostim"},
            {"vkn": "1111111111", "kaynak": "ivedik"},
            {"vkn": "2222222222", "kaynak": "ostim"},
            {"vkn": "3333333333", "kaynak": "baskent"},
        ]
        sonuc = mukerrer_orani(kayitlar)
        assert sonuc["toplam"] == 4
        assert sonuc["benzersiz"] == 3
        assert sonuc["mukerrer"] == 1
        assert sonuc["oran"] == 0.25

    def test_eksik_anahtar(self):
        """Anahtarı olmayan kayıtlar benzersiz sayılır."""
        kayitlar = [
            {"vkn": "1111111111", "kaynak": "ostim"},
            {"kaynak": "ivedik"},  # vkn yok
            {"vkn": "2222222222", "kaynak": "baskent"},
        ]
        sonuc = mukerrer_orani(kayitlar)
        assert sonuc["toplam"] == 3
        assert sonuc["benzersiz"] == 3
        assert sonuc["mukerrer"] == 0
        assert sonuc["oran"] == 0.0

    def test_ozel_anahtar(self):
        """Farklı anahtar ile çalışır."""
        kayitlar = [
            {"email": "a@x.com", "kaynak": "ostim"},
            {"email": "a@x.com", "kaynak": "ivedik"},
            {"email": "b@x.com", "kaynak": "ostim"},
        ]
        sonuc = mukerrer_orani(kayitlar, anahtar="email")
        assert sonuc["toplam"] == 3
        assert sonuc["benzersiz"] == 2
        assert sonuc["mukerrer"] == 1
        assert sonuc["oran"] == 0.3333  # 1/3 rounded to 4 decimal places

    def test_kaynak_bazli_kirilim(self):
        """Kaynak bazlı kırılım doğru hesaplanır."""
        kayitlar = [
            {"vkn": "111", "kaynak": "ostim"},
            {"vkn": "111", "kaynak": "ostim"},
            {"vkn": "222", "kaynak": "ivedik"},
        ]
        sonuc = mukerrer_orani(kayitlar)
        assert sonuc["kaynak_bazli"] == {"ostim": 2, "ivedik": 1}

    def test_kaynak_olmayan_kayit(self):
        """Kaynak alan yoksa 'bilinmiyor' kullanılır."""
        kayitlar = [
            {"vkn": "111"},
            {"vkn": "111"},
        ]
        sonuc = mukerrer_orani(kayitlar)
        assert sonuc["kaynak_bazli"] == {"bilinmiyor": 2}

    def test_kaynak_source_ali(self):
        """'source' alias'ı da tanınır."""
        kayitlar = [
            {"vkn": "111", "source": "ostim"},
            {"vkn": "222", "source": "ivedik"},
        ]
        sonuc = mukerrer_orani(kayitlar)
        assert sonuc["kaynak_bazli"] == {"ostim": 1, "ivedik": 1}

    def test_oran_araligi(self):
        """Oran her zaman [0, 1] aralığında olmalıdır."""
        kayitlar = [
            {"vkn": "111"},
            {"vkn": "222"},
        ]
        sonuc = mukerrer_orani(kayitlar)
        assert 0.0 <= sonuc["oran"] <= 1.0


# ---------------------------------------------------------------------------
# Legacy fonksiyon
# ---------------------------------------------------------------------------

class TestMukerrerOraniLegacy:
    """Legacy tuple arayüz testleri."""

    def test_legacy_tuple_donusum(self):
        """Legacy fonksiyon tuple döndürür ve değerleri doğru."""
        kayitlar = [
            {"vkn": "111"},
            {"vkn": "111"},
            {"vkn": "222"},
        ]
        toplam, benzersiz, mukerrer, oran, kaynak_bazli = mukerrer_orani_legacy(kayitlar)
        assert toplam == 3
        assert benzersiz == 2
        assert mukerrer == 1
        assert oran == 0.3333  # 1/3 rounded to 4 decimal places
        assert kaynak_bazli == {"bilinmiyor": 3}

    def test_legacy_bos(self):
        """Legacy fonksiyon boş liste için sıfır döndürür."""
        toplam, benzersiz, mukerrer, oran, kaynak_bazli = mukerrer_orani_legacy([])
        assert toplam == 0
        assert benzersiz == 0
        assert mukerrer == 0
        assert oran == 0.0
        assert kaynak_bazli == {}


# ---------------------------------------------------------------------------
# DedupResult dataclass
# ---------------------------------------------------------------------------

class TestDedupResult:
    """DedupResult dataclass testleri."""

    def test_to_dict(self):
        """to_dict doğru formatta dict döndürür."""
        result = DedupResult(
            toplam=5,
            benzersiz=3,
            mukerrer=2,
            oran=0.4,
            kaynak_bazli={"ostim": 3, "ivedik": 2},
        )
        d = result.to_dict()
        assert d == {
            "toplam": 5,
            "benzersiz": 3,
            "mukerrer": 2,
            "oran": 0.4,
            "kaynak_bazli": {"ostim": 3, "ivedik": 2},
        }

    def test_oran_yuvarlama(self):
        """Oran 4 ondalık basamağa yuvarlanır."""
        result = DedupResult(
            toplam=3,
            benzersiz=1,
            mukerrer=2,
            oran=0.6666666666666666,
        )
        d = result.to_dict()
        assert d["oran"] == 0.6667
