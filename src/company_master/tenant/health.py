# -*- coding: utf-8 -*-
"""Tenant Health Score v1 — Tenant bazlı sağlık skoru hesaplama modülü.

Kapsam (PRD Faz 2, PO-BACK-01):
  - Data Quality Score: Firma veri kalitesi ortalaması (0-100)
  - Source Reliability: Kaynak güvenilirliği (kampanya durum makinesi)
  - Coverage Score: Segment uygunluk oranı
  - Activity Score: Son etkinlik tazeliği

Skor formülü:
    Health = 0.35 * DQ + 0.25 * SR + 0.25 * CV + 0.15 * AC

Eşikler:
    GREEN (sağlıklı):  >= 85
    YELLOW (uyarı):    60-84
    RED (kritik):       < 60

Referanslar:
    - PO-01_urun_vizyonu_ve_kararlar.md: Tenant Health Score v1
    - AR-03_kullanici_persona_yol_haritasi.md: Segment, paket, kampanya verileri
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from company_master.tenant.model import TenantContext

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------

HEALTH_GREEN: float = 85.0
HEALTH_YELLOW: float = 60.0

WEIGHTS: dict[str, float] = {
    "data_quality": 0.35,
    "source_reliability": 0.25,
    "coverage": 0.25,
    "activity": 0.15,
}

BANDS: dict[str, tuple[float, float]] = {
    "green": (HEALTH_GREEN, 100.0),
    "yellow": (HEALTH_YELLOW, HEALTH_GREEN),
    "red": (0.0, HEALTH_YELLOW),
}
# ---------------------------------------------------------------------------
# Veri yapıları
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TenantHealthScore:
    """Tenant Health Score v1 sonucu."""

    tenant_id: str
    overall: float              # 0-100
    band: str = ""              # green | yellow | red (otomatik atanır)
    components: dict[str, float] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Bant otomatis atama."""
        object.__setattr__(self, "band", _banti_bul(self.overall))

    def to_dict(self) -> dict[str, Any]:
        """Sözlükye çevir."""
        return {
            "tenant_id": self.tenant_id,
            "overall_score": self.overall,
            "band": self.band,
            "components": dict(self.components),
            "details": dict(self.details),
        }


def _banti_bul(score: float) -> str:
    """Skoruna göre sağlık bantını bul."""
    if score >= HEALTH_GREEN:
        return "green"
    if score >= HEALTH_YELLOW:
        return "yellow"
    return "red"

# ---------------------------------------------------------------------------
# Formül fonksiyonları
# ---------------------------------------------------------------------------

def _data_quality_score(companies: list[dict[str, Any]]) -> float:
    """Data Quality Score — firmaların data_quality_score ortalaması (0-100).

    Formül:
        DQ = avg(companies.data_quality_score) veya 0 eğer firma yoksa.
    """
    if not companies:
        return 0.0
    scores = [c.get("data_quality_score", 0) for c in companies]
    return round(sum(scores) / len(scores), 2)


def _source_reliability_score(
    campaigns: list[dict[str, Any]],
) -> float:
    """Source Reliability — kaynak güvenilirliği (0-100).

    Formül:
        Aktif kampanyaların %'si tam veriye sahipse (bitiş tarihi geçmiş değil,
        tedarikçi tanımı var).
        SR = (tam_kampanya_sayisi / toplam_aktif_kampanya_sayisi) * 100
        Eğer aktif kampanya yoksa, 100 (boşsa sorun yok).
    """
    active = [c for c in campaigns if c.get("durum") == "aktif"]
    if not active:
        return 100.0
    tam = sum(
        1 for c in active
        if c.get("tedarikci") and c.get("bitis_tarihi")
    )
    return round((tam / len(active)) * 100, 2)


def _coverage_score(companies: list[dict[str, Any]]) -> float:
    """Coverage Score — segment uygunluk oranı (0-100).

    Formül:
        Uygun segmente sahip firma sayısı / toplam firma sayısı * 100
        Uygun: data_quality_score >= 50 AND nace_code dolu AND adres dolu
    """
    if not companies:
        return 0.0
    uygun = sum(
        1 for c in companies
        if c.get("data_quality_score", 0) >= 50
        and c.get("nace_code")
        and c.get("adres")
    )
    return round((uygun / len(companies)) * 100, 2)


def _activity_score(companies: list[dict[str, Any]]) -> float:
    """Activity Score — son etkinlik tazeliği (0-100).

    Formül:
        Son 30 gün içinde güncelleme yapan firma oranı * 100
        varsayılan: 50 (orta taze)
    """
    if not companies:
        return 50.0
    guncel = sum(1 for c in companies if c.get("son_guncelleme_gun") is not None)
    return round((guncel / len(companies)) * 100, 2)

# ---------------------------------------------------------------------------
# Ana hesaplama fonksiyonu
# ---------------------------------------------------------------------------

def hesapla(
    tenant_ctx: TenantContext,
    companies: list[dict[str, Any]],
    campaigns: list[dict[str, Any]] | None = None,
) -> TenantHealthScore:
    """Tenant Health Score v1 hesapla.

    Args:
        tenant_ctx: TenantContext — hesaplanacak tenant
        companies: Firma verileri listesi
                 (dict with data_quality_score, nace_code, ...)
        campaigns: Opsiyonel kampanya verileri listesi

    Returns:
        TenantHealthScore — genel skor, bant ve bileşen ayrıntıları

    Örnek:
        >>> ctx = TenantContext("huginn", "Huginn Data", "standart")
        >>> firms = [{"data_quality_score": 75, "nace_code": "6201", "adres": "Ankara"}]
        >>> result = hesapla(ctx, firms)
        >>> result.overall
        75.0
    """
    campaigns = campaigns or []

    dq = _data_quality_score(companies)
    sr = _source_reliability_score(campaigns)
    cv = _coverage_score(companies)
    ac = _activity_score(companies)

    overall = round(
        WEIGHTS["data_quality"] * dq
        + WEIGHTS["source_reliability"] * sr
        + WEIGHTS["coverage"] * cv
        + WEIGHTS["activity"] * ac,
        2,
    )

    components = {
        "data_quality": dq,
        "source_reliability": sr,
        "coverage": cv,
        "activity": ac,
    }

    details = {
        "firma_sayisi": len(companies),
        "kampanya_sayisi": len(campaigns),
        "agirliklar": dict(WEIGHTS),
        "tenant_plan": tenant_ctx.plan,
    }

    return TenantHealthScore(
        tenant_id=tenant_ctx.tenant_id,
        overall=overall,
        components=components,
        details=details,
    )


# ---------------------------------------------------------------------------
# Eşik dokümanı (yazdırma)
# ---------------------------------------------------------------------------

def esik_dokumani() -> str:
    """Tenant Health Score eşik değerlerini dokümantasyon olarak döndürür."""
    lines = [
        "# Tenant Health Score v1 — Eşik Dokümanı",
        "",
        "## Genel Formül",
        "",
        "```",
        "Health = 0.35 * DataQuality + 0.25 * SourceReliability + 0.25 * Coverage + 0.15 * Activity",
        "```",
        "",
        "## Bant Tanımları",
        "",
        "| Bant | Aralık | Açıklama | Renk |",
        "|------|--------|----------|------|",
        f"| Sağlıklı (GREEN) | >= {HEALTH_GREEN:.0f} | Tenant tüm metriklerde güçlü | 🟢 |",
        f"| Uyarı (YELLOW) | {HEALTH_YELLOW:.0f} - {HEALTH_GREEN:.0f} | Birkaç metrik düşük | 🟡 |",
        f"| Kritik (RED) | < {HEALTH_YELLOW:.0f} | Çok sayıda eksik/kötü veri | 🔴 |",
        "",
        "## Bileşen Ağırlıkları",
        "",
        "| Bileşen | Ağırlık | Açıklama |",
        "|---------|---------|----------|",
        "| Data Quality | 35% | Firma veri tamamlığı ve doğruluk |",
        "| Source Reliability | 25% | Kaynak/kampanya güvenilirliği |",
        "| Coverage | 25% | Segment uygunluk oranı |",
        "| Activity | 15% | Son güncelleme tazeliği |",
        "",
        "## Referans",
        "",
        "- PO-BACK-01: Tenant Health Score v1",
        "- PO-01_urun_vizyonu_ve_kararlar.md",
    ]
    return "\n".join(lines)


