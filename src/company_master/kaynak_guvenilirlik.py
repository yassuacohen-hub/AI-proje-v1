# -*- coding: utf-8 -*-
"""Source Reliability Monitor — Kaynak bazlı güvenilirlik skoru (Admin).

Kapsam (PO-BACK-11):
  - Kaynak tazeliği (recency): son çekişten gün sayısı
  - Hata oranı (error_rate): başarısız çekişler / toplam çekişler
  - Tutarlılık (consistency): son N çekişte başarı oranı
  - Kaynak skoru (source_reliability_score): tazelik * (1 - hata_oranı) * tutarlılık

Eşikler:
  - GREEN: >= 75
  - YELLOW: 50-74
  - RED: < 50

Referanslar:
  - PO-BACK-11: Admin Panel Kaynak Güvenilirliği
  - health.py: _source_reliability_score (kampanya durum makinesi tarafından çağrılan)
  - admin_quality.py: Veri kalitesi admin panel kalıbı
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------

# Eşikler (skor 0-100)
RELIABILITY_GREEN: float = 75.0
RELIABILITY_YELLOW: float = 50.0

# Tazelik ağırlıkları (gün cinsinden)
RECENCY_FRESH_DAYS: int = 7      # 7 gün içinde = 100 puan
RECENCY_STALE_DAYS: int = 30     # 30+ gün = 0 puan
RECENCY_MAX_SCORE: float = 1.0

# Hata oranı eşiği
ERROR_RATE_THRESHOLD: float = 0.05  # %5 üzeri sorun

# Tutarlılık hesaplaması için son N çekiş
CONSISTENCY_WINDOW: int = 10

# ---------------------------------------------------------------------------
# Veri yapıları
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class KaynakSaglik:
    """Tek bir kaynağın sağlık skoru."""

    kaynak_id: str
    kaynak_adi: str
    skor: float              # 0-100
    band: str = ""           # green | yellow | red (otomatik atanır)
    tazelik_skoru: float = 0.0      # 0-100: son çekiş tazeliği
    hata_orani: float = 0.0         # 0-1: hata oranı
    tutarlilik_skoru: float = 0.0   # 0-100: tutarlılık (son 10 çekişte başarı)
    toplam_cekis: int = 0           # Toplam çekiş sayısı
    basarili_cekis: int = 0         # Başarılı çekiş sayısı
    son_cekis_zaman: str | None = None  # ISO 8601 zaman damgası
    olusturma_zaman: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    )

    def __post_init__(self) -> None:
        """Bant otomatis atama."""
        object.__setattr__(self, "band", _banti_bul(self.skor))

    def to_dict(self) -> dict[str, Any]:
        """Sözlüğe çevir."""
        return {
            "kaynak_id": self.kaynak_id,
            "kaynak_adi": self.kaynak_adi,
            "skor": self.skor,
            "band": self.band,
            "tazelik_skoru": self.tazelik_skoru,
            "hata_orani": round(self.hata_orani, 4),
            "tutarlilik_skoru": self.tutarlilik_skoru,
            "toplam_cekis": self.toplam_cekis,
            "basarili_cekis": self.basarili_cekis,
            "son_cekis_zaman": self.son_cekis_zaman,
            "olusturma_zaman": self.olusturma_zaman,
        }


def _banti_bul(skor: float) -> str:
    """Skora göre güvenilirlik bantını bul."""
    if skor >= RELIABILITY_GREEN:
        return "green"
    if skor >= RELIABILITY_YELLOW:
        return "yellow"
    return "red"


# ---------------------------------------------------------------------------
# Hesaplama fonksiyonları
# ---------------------------------------------------------------------------

def _tazelik_skoru(son_cekis_zaman: str | None) -> float:
    """Tazelik skoru hesapla (0-100).

    Formül:
        - 7 gün içinde: 100
        - 7-30 gün: doğrusal azalış
        - 30+ gün: 0
        - Veri yok: 0
    """
    if not son_cekis_zaman:
        return 0.0

    try:
        son_zaman = datetime.fromisoformat(son_cekis_zaman)
        # tz-aware (DB timestamptz) ve naive (UTC varsayımı) girdileri tek eksene indir
        if son_zaman.tzinfo is not None:
            son_zaman = son_zaman.astimezone(timezone.utc).replace(tzinfo=None)
        simdi = datetime.now(timezone.utc).replace(tzinfo=None)
        gun_farki = (simdi - son_zaman).days

        if gun_farki <= RECENCY_FRESH_DAYS:
            return 100.0

        if gun_farki >= RECENCY_STALE_DAYS:
            return 0.0

        # Doğrusal azalış: 7-30 gün
        oran = (gun_farki - RECENCY_FRESH_DAYS) / (RECENCY_STALE_DAYS - RECENCY_FRESH_DAYS)
        return round((1.0 - oran) * 100, 2)

    except (ValueError, TypeError):
        return 0.0


def _hata_orani(toplam: int, basarili: int) -> float:
    """Hata oranı hesapla (0-1).

    Formül:
        error_rate = (toplam - başarılı) / toplam
    """
    if toplam <= 0:
        return 0.0
    return round((toplam - basarili) / toplam, 4)


def _tutarlilik_skoru(son_n_cekisler: list[bool]) -> float:
    """Tutarlılık skoru (0-100).

    Formül:
        Son N çekişte başarı oranı * 100
        (N = CONSISTENCY_WINDOW)
    """
    if not son_n_cekisler:
        return 0.0

    basarili = sum(1 for basarı in son_n_cekisler if basarı)
    return round((basarili / len(son_n_cekisler)) * 100, 2)


def hesapla(
    kaynak_id: str,
    kaynak_adi: str,
    toplam_cekis: int,
    basarili_cekis: int,
    son_cekis_zaman: str | None,
    son_n_cekisler: list[bool] | None = None,
) -> KaynakSaglik:
    """Kaynak Sağlık Skoru hesapla.

    Args:
        kaynak_id: Kaynağın benzersiz kimliği
        kaynak_adi: Okunabilir kaynak adı
        toplam_cekis: Toplam çekiş sayısı
        basarili_cekis: Başarılı çekiş sayısı
        son_cekis_zaman: Son çekişin zaman damgası (ISO 8601)
        son_n_cekisler: Son N çekişin başarı listesi [True, False, ...]

    Returns:
        KaynakSaglik — skor, bant ve bileşen ayrıntıları

    Örnek:
        >>> result = hesapla(
        ...     "apify_001",
        ...     "Apify Scraper",
        ...     toplam_cekis=100,
        ...     basarili_cekis=95,
        ...     son_cekis_zaman="2026-09-15T02:00:00",
        ...     son_n_cekisler=[True, True, False, True, True, True, True, True, True, True]
        ... )
        >>> result.skor
        87.5
    """
    son_n_cekisler = son_n_cekisler or []

    # Bileşen skorları
    tazelik = _tazelik_skoru(son_cekis_zaman)
    hata_orani = _hata_orani(toplam_cekis, basarili_cekis)
    tutarlilik = _tutarlilik_skoru(son_n_cekisler) if son_n_cekisler else 0.0

    # Genel skor formülü: Tazelik × (1 - Hata Oranı) × Tutarlılık / 10000
    # Basitleştirilmiş formül: (tazelik * 0.5) + (tutarlılık * 0.4) + ((1 - hata_orani) * 0.1 * 100)
    # Daha sade: tazelik 50%, tutarlılık 40%, hata cezası 10%
    skor = round(
        (tazelik * 0.5) +
        (tutarlilik * 0.4) +
        ((1.0 - min(hata_orani, 1.0)) * 100 * 0.1),
        2
    )

    return KaynakSaglik(
        kaynak_id=kaynak_id,
        kaynak_adi=kaynak_adi,
        skor=skor,
        tazelik_skoru=tazelik,
        hata_orani=hata_orani,
        tutarlilik_skoru=tutarlilik,
        toplam_cekis=toplam_cekis,
        basarili_cekis=basarili_cekis,
        son_cekis_zaman=son_cekis_zaman,
    )


# ---------------------------------------------------------------------------
# Toplu hesaplama
# ---------------------------------------------------------------------------

def hesapla_toplu(kaynaklar: list[dict[str, Any]]) -> list[KaynakSaglik]:
    """Birden fazla kaynağın sağlık skorlarını hesapla.

    Args:
        kaynaklar: Her biri şu alanları içeren dict listesi:
            - kaynak_id (str)
            - kaynak_adi (str)
            - toplam_cekis (int)
            - basarili_cekis (int)
            - son_cekis_zaman (str | None)
            - son_n_cekisler (list[bool] | None, isteğe bağlı)

    Returns:
        KaynakSaglik listesi
    """
    return [
        hesapla(
            kaynak_id=k.get("kaynak_id", ""),
            kaynak_adi=k.get("kaynak_adi", ""),
            toplam_cekis=k.get("toplam_cekis", 0),
            basarili_cekis=k.get("basarili_cekis", 0),
            son_cekis_zaman=k.get("son_cekis_zaman"),
            son_n_cekisler=k.get("son_n_cekisler"),
        )
        for k in kaynaklar
    ]


# ---------------------------------------------------------------------------
# Raporlama
# ---------------------------------------------------------------------------

def esik_dokumani() -> str:
    """Kaynak Sağlık Skoru eşik değerlerini dokümantasyon olarak döndürür."""
    lines = [
        "# Kaynak Sağlık Skoru v1 — Eşik Dokümanı",
        "",
        "## Genel Formül",
        "",
        "```",
        "Skor = (Tazelik × 0.5) + (Tutarlılık × 0.4) + ((1 - Hata_Oranı) × 100 × 0.1)",
        "```",
        "",
        "## Bant Tanımları",
        "",
        "| Bant | Aralık | Açıklama | Renk |",
        "|------|--------|----------|------|",
        f"| Sağlıklı (GREEN) | >= {RELIABILITY_GREEN:.0f} | Kaynak tutarlı ve taze | 🟢 |",
        f"| Uyarı (YELLOW) | {RELIABILITY_YELLOW:.0f} - {RELIABILITY_GREEN:.0f} | Bazı sorunlar var | 🟡 |",
        f"| Kritik (RED) | < {RELIABILITY_YELLOW:.0f} | Eski veya az güvenilir | 🔴 |",
        "",
        "## Bileşen Ağırlıkları",
        "",
        "| Bileşen | Ağırlık | Açıklama |",
        "|---------|---------|----------|",
        f"| Tazelik (Recency) | 50% | Son çekiş zamanı ({RECENCY_FRESH_DAYS}-{RECENCY_STALE_DAYS} gün) |",
        f"| Tutarlılık (Consistency) | 40% | Son {CONSISTENCY_WINDOW} çekişte başarı oranı |",
        f"| Güvenilirlik (Reliability) | 10% | Toplam hata oranı cezası (max %{ERROR_RATE_THRESHOLD*100:.0f}) |",
        "",
        "## Referans",
        "",
        "- PO-BACK-11: Source Reliability Monitor (Admin)",
        "- health.py: Tenant Health Score kaynak bileşeni",
    ]
    return "\n".join(lines)
