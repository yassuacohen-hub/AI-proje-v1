# -*- coding: utf-8 -*-
"""Duplicate Rate Metrics — Admin Dashboard veri katmanı (PO-BACK-09).

Bu modül, verilen kayıt listesi üzerinden VKN (veya başka bir anahtar)
bazlı mükerrer oran hesaplar. Mevcut `vector/service.deduplicate_by_vkn`
ve `etl/multi_osb_merger.deduplicate_companies` mantığıyla tutarlı
çalışır (import etmez, saf fonksiyon).

Kullanım:
    from company_master.dedup_metrics import mukerrer_orani

    kayitlar = [
        {"vkn": "1234567890", "kaynak": "ostim"},
        {"vkn": "1234567890", "kaynak": "ivedik"},
        {"vkn": "0987654321", "kaynak": "ostim"},
    ]
    sonuc = mukerrer_orani(kayitlar)
    # {'toplam': 3, 'benzersiz': 2, 'mukerrer': 1, 'oran': 0.3333, 'kaynak_bazli': {'ostim': 2, 'ivedik': 1}}

"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DedupResult:
    """Mükerrer oran hesaplama sonucu."""

    toplam: int
    benzersiz: int
    mukerrer: int
    oran: float
    kaynak_bazli: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """API/UI için serileştirilebilir sözlük."""
        return {
            "toplam": self.toplam,
            "benzersiz": self.benzersiz,
            "mukerrer": self.mukerrer,
            "oran": round(self.oran, 4),
            "kaynak_bazli": self.kaynak_bazli,
        }


def _anahtar_al(kayit: dict[str, Any], anahtar: str) -> Any:
    """Kayıttan anahtar değerini güvenli alır."""
    return kayit.get(anahtar)


def _kaynak_al(kayit: dict[str, Any]) -> str:
    """Kayıttan kaynak alanını alır (yoksa 'bilinmiyor')."""
    return kayit.get("kaynak", kayit.get("source", "bilinmiyor"))


def mukerrer_orani(
    kayitlar: list[dict[str, Any]],
    anahtar: str = "vkn",
) -> dict[str, Any]:
    """
    Verilen kayıt listesinde, belirtilen anahtara göre mükerrer oran hesaplar.

    Args:
        kayitlar: Firma kayıtları listesi (her kayıt dict).
        anahtar: Benzersizlik için kullanılacak alan adı (varsayılan: 'vkn').

    Returns:
        Dict: {
            "toplam": int,
            "benzersiz": int,
            "mukerrer": int,
            "oran": float (0-1 arası),
            "kaynak_bazli": dict[str, int]  # kaynak -> kayıt sayısı
        }

    Notes:
        - Anahtarı olmayan kayıtlar 'mukerrer' sayılmaz, 'benzersiz' sayılır.
        - Bu tutarlılık `multi_osb_merger.deduplicate_companies` ile sağlanır:
          VKN yoksa ilk kayıt alınır (drop_duplicates keep='first').
    """
    if not kayitlar:
        return DedupResult(
            toplam=0,
            benzersiz=0,
            mukerrer=0,
            oran=0.0,
            kaynak_bazli={},
        ).to_dict()

    # Kaynak bazlı kırılım
    kaynak_sayac: Counter[str] = Counter()
    for k in kayitlar:
        kaynak_sayac[_kaynak_al(k)] += 1

    # Anahtar değerlerini topla
    anahtar_degerleri = [_anahtar_al(k, anahtar) for k in kayitlar]
    anahtar_sayac: Counter[Any] = Counter(anahtar_degerleri)

    # Benzersiz: anahtarı olan ve tek geçenler + anahtarı olmayanlar
    benzersiz = 0
    mukerrer = 0

    for deger, sayi in anahtar_sayac.items():
        if deger is None:
            # Anahtarı olmayan kayıtlar benzersiz sayılır (multi_osb_merger tutarlılığı)
            benzersiz += sayi
        elif sayi == 1:
            benzersiz += 1
        else:
            # Mükerrer: aynı anahtardan birden fazla varsa, ilki benzersiz, kalanlar mükerrer
            benzersiz += 1
            mukerrer += sayi - 1

    toplam = len(kayitlar)
    oran = mukerrer / toplam if toplam > 0 else 0.0

    return DedupResult(
        toplam=toplam,
        benzersiz=benzersiz,
        mukerrer=mukerrer,
        oran=oran,
        kaynak_bazli=dict(kaynak_sayac),
    ).to_dict()


# ---------------------------------------------------------------------------
# Yardımcı: geri dönüş uyumluluğu için legacy fonksiyon (opsiyonel)
# ---------------------------------------------------------------------------

def mukerrer_orani_legacy(
    kayitlar: list[dict[str, Any]],
    anahtar: str = "vkn",
) -> tuple[int, int, int, float, dict[str, int]]:
    """
    Legacy tuple interface (toplam, benzersiz, mukerrer, oran, kaynak_bazli).
    Yeni kod `mukerrer_orani` (dict dönen) kullanılmalı.
    """
    sonuc = mukerrer_orani(kayitlar, anahtar)
    return (
        sonuc["toplam"],
        sonuc["benzersiz"],
        sonuc["mukerrer"],
        sonuc["oran"],
        sonuc["kaynak_bazli"],
    )
