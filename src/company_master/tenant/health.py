# -*- coding: utf-8 -*-
"""Tenant Health Score v1 — Tenant bazlı sağlık skoru hesaplama modülü.

Kapsam (PRD Faz 2, PO-BACK-01):
  - Kimlik Dosyası Tamlığı: firmaların ``identity_completeness`` (0-10)
    ortalamasının **ulaşılabilir tavana oranı** — yüzde (D-250/7)
  - Source Reliability: Kaynak güvenilirliği (kampanya durum makinesi)
  - Coverage Score: Segment uygunluk oranı
  - Activity Score: Son etkinlik tazeliği

Skor formülü:
    Health = 0.35 * DQ + 0.25 * SR + 0.25 * CV + 0.15 * AC

Dört bileşenin tamamı **yüzde** (0-100); bu yüzden toplanabilirler. Tamlık
puanı 0-10 ölçeğinde üretildiği için burada tavana bölünerek yüzdeye çevrilir
(`sunum.tavan_getir()`). Tavan sabit yazılmaz; ağırlık seti değişince kendi
kendine güncellenir.

Eşikler (yüzde):
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

from company_master.sunum import tavan_getir
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

def _identity_completeness(companies: list[dict[str, Any]]) -> float:
    """Kimlik dosyası tamlığı — ölçülmüş firmaların tavana oranı, yüzde.

    Formül:
        DQ = avg(olculmus.identity_completeness) / ulasilabilir_tavan * 100

    D-249: ölçülmemiş firma (None) ortalamaya 0 olarak **girmez**, dışlanır.
    D-250/7: 0-10'luk puan tavana bölünmeden diğer yüzde bileşenlerle
    toplanamaz. Tavanı aşan değer ölçek hatasıdır; sessizce kırpılmaz.
    """
    olculmus = [
        c["identity_completeness"] for c in companies
        if c.get("identity_completeness") is not None
    ]
    if not olculmus:
        return 0.0
    tavan = tavan_getir()
    ortalama = sum(olculmus) / len(olculmus)
    if ortalama > tavan:
        raise ValueError(
            f"tamlik ortalamasi ({ortalama:.2f}) ulasilabilir tavani "
            f"({tavan:.2f}) asiyor - veri 0-100 olceginde olabilir"
        )
    return round(ortalama / tavan * 100, 2)


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
        Uygun: tamlık >= tavanın yarısı AND nace_code dolu AND adres dolu

    Eşik tavandan türetilir; sabit yazılsa ölçek değişince hiçbir firma
    uygun sayılmaz ve skor sessizce daima 0 döner.
    """
    if not companies:
        return 0.0
    esik = tavan_getir() / 2
    uygun = sum(
        1 for c in companies
        if (c.get("identity_completeness") or 0) >= esik
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
                 (dict with identity_completeness [0-10], nace_code, ...)
                 Ölçülmemiş firma ``None`` taşır, 0 taşımaz (D-249).
        campaigns: Opsiyonel kampanya verileri listesi

    Returns:
        TenantHealthScore — genel skor (yüzde), bant ve bileşen ayrıntıları

    Örnek:
        >>> ctx = TenantContext("huginn", "Huginn Data", "standart")
        >>> tam = tavan_getir()  # ulasilabilir tavan, sabit degil
        >>> firms = [{"identity_completeness": tam, "nace_code": "6201",
        ...           "adres": "Ankara", "son_guncelleme_gun": 3}]
        >>> hesapla(ctx, firms).band
        'green'
    """
    campaigns = campaigns or []

    dq = _identity_completeness(companies)
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
        f"| Kimlik Dosyası Tamlığı | 35% | Tamlık ortalamasının ulaşılabilir "
        f"tavana ({tavan_getir():.2f}) oranı, yüzde |",
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


