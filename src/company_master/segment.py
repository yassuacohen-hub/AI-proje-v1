# -*- coding: utf-8 -*-
"""Segment Eligibility Skoru + Onay Akışı (PO-BACK-02).

Bu modül, her firmanın segment kriterlerine göre uygunluk skorunu hesaplar
ve onay akışı durumunu üretir.

Kullanım:
    from company_master.segment import calculate_segment_eligibility, onay_aciklama

Referanslar:
    - PO-01_urun_vizyonu_ve_kararlar.md: PO-BACK-02
    - data/demo/segment_demo.jsonl: Segment tanımı ve kriterleri
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Alan eşleme: şirket verisindeki alan adlarını segment kriterleriyle eşleştir
# ---------------------------------------------------------------------------

SEKTOR_ALANLARI = frozenset({"sektor", "sector", "nace_code", "nace", "industri"})
FIRMA_TIPI_ALANLARI = frozenset({"firma_tipi", "company_type", "tip", "firmaTipi"})
HACIM_ALANLARI = frozenset({"min_hacim", "revenue", "hacim", "cari_hacim", "annual_revenue"})
TURU_ALANLARI = frozenset({"turu", "type", "tur"})


# ---------------------------------------------------------------------------
# Veri yapıları
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SegmentEligibilite:
    """Tek segment için uygunluk sonucu."""

    segment_id: str
    segment_name: str
    eligible: bool
    score: float
    matched_criteria: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "segment_name": self.segment_name,
            "eligible": self.eligible,
            "score": self.score,
            "matched_criteria": list(self.matched_criteria),
            "missing_fields": list(self.missing_fields),
            "details": dict(self.details),
        }


# ---------------------------------------------------------------------------
# Yardımcı
# ---------------------------------------------------------------------------

def _esit(metin1: Any, metin2: Any) -> bool:
    if metin1 is None or metin2 is None:
        return False
    return str(metin1).strip().lower() == str(metin2).strip().lower()


def _sayi_degeri(deger: Any) -> float | None:
    if deger is None:
        return None
    try:
        return float(deger)
    except (ValueError, TypeError):
        return None


def _alan_bul(company: dict[str, Any], alan_kume: frozenset[str]) -> str | None:
    for alan in alan_kume:
        if alan in company and company[alan] is not None:
            return str(company[alan])
    return None


def _kriter_eslesme(
    sart: dict[str, Any],
    company: dict[str, Any],
) -> tuple[bool, str | None]:
    for anahtar, deger in sart.items():
        key = anahtar.lower()

        if key in HACIM_ALANLARI:
            company_revenue = _sayi_degeri(_alan_bul(company, HACIM_ALANLARI))
            min_hacim = _sayi_degeri(deger)
            if company_revenue is None or min_hacim is None:
                return False, anahtar
            if company_revenue < min_hacim:
                return False, anahtar
            return True, None

        if key in SEKTOR_ALANLARI:
            if not _esit(_alan_bul(company, SEKTOR_ALANLARI), deger):
                return False, anahtar
            return True, None

        if key in FIRMA_TIPI_ALANLARI:
            if not _esit(_alan_bul(company, FIRMA_TIPI_ALANLARI), deger):
                return False, anahtar
            return True, None

        if key in TURU_ALANLARI:
            if not _esit(_alan_bul(company, TURU_ALANLARI), deger):
                return False, anahtar
            return True, None

        if not _esit(company.get(anahtar), deger):
            return False, anahtar

    return True, None


# ---------------------------------------------------------------------------
# Ana hesaplama fonksiyonları
# ---------------------------------------------------------------------------

def calculate_segment_eligibility(
    company: dict[str, Any],
    segments: list[dict[str, Any]],
) -> list[SegmentEligibilite]:
    """
    Bir şirketin tüm segmentlere göre uygunluk skorunu hesaplar.

    Her segmentin kriterleri kontrol edilir:
        - Eşleşen kriter sayısı / toplam kriter sayısı = skor (%)
        - Skoru >= 95 ise `eligible` = True

    Returns:
        SegmentEligibilite listesi (skor düşük sıraya göre).
    """
    sonuclar: list[SegmentEligibilite] = []

    for segment in segments:
        segment_id = segment.get("segment_id", "")
        segment_name = segment.get("name", "")
        criteria = segment.get("criteria", {})

        if not criteria:
            sonuclar.append(SegmentEligibilite(
                segment_id=segment_id,
                segment_name=segment_name,
                eligible=True,
                score=100.0,
                matched_criteria=[],
                missing_fields=[],
                details={"note": "Kriter tanımı yok, varsayılan uygun"},
            ))
            continue

        matched: list[str] = []
        missing: list[str] = []

        for kriter_adi, kriter_degeri in criteria.items():
            eslesme, eksik = _kriter_eslesme({kriter_adi: kriter_degeri}, company)
            if eslesme:
                matched.append(kriter_adi)
            else:
                missing.append(eksik or kriter_adi)

        toplam = len(criteria)
        skor = (len(matched) / toplam * 100) if toplam > 0 else 100.0
        skor = round(skor, 2)

        sonuclar.append(SegmentEligibilite(
            segment_id=segment_id,
            segment_name=segment_name,
            eligible=skor >= 95.0,
            score=skor,
            matched_criteria=matched,
            missing_fields=missing,
            details={
                "criteria": dict(criteria),
                "matched_count": len(matched),
                "total_count": toplam,
            },
        ))

    sonuclar.sort(key=lambda x: x.score, reverse=True)
    return sonuclar


def aggregate_eligibility(
    company: dict[str, Any],
    segments: list[dict[str, Any]],
) -> dict[str, Any]:
    """Bir şirketin tüm segmentler için özet uygunluk bilgisi."""
    sonuclar = calculate_segment_eligibility(company, segments)
    toplam = len(sonuclar)
    uygun_sayisi = sum(1 for s in sonuclar if s.eligible)
    genel_skor = round(sum(s.score for s in sonuclar) / toplam, 2) if toplam > 0 else 0.0
    onay = "onaylı" if uygun_sayisi >= max(1, toplam * 0.8) else "eksik alan"

    return {
        "toplam_segment": toplam,
        "uygun_segment_sayisi": uygun_sayisi,
        "genel_skor": genel_skor,
        "onay_durumu": onay,
        "segment_detaylari": [s.to_dict() for s in sonuclar],
    }


def onay_aciklama(company: dict[str, Any], segments: list[dict[str, Any]]) -> str:
    """Onay akışı için insan okunabilir açıklama üretir."""
    agg = aggregate_eligibility(company, segments)
    satir = [f"📋 {company.get('company_name', 'Bilinmeyen Şirket')} — Segment Uygunluk Değerlendirmesi"]
    satir.append(f"   Toplam segment: {agg['toplam_segment']}, Uygun: {agg['uygun_segment_sayisi']}, Genel skor: {agg['genel_skor']:.1f}%")
    satir.append(f"   Onay durumu: {agg['onay_durumu']}")

    for detay in agg["segment_detaylari"]:
        if not detay["eligible"]:
            eksik = ", ".join(detay["missing_fields"]) if detay["missing_fields"] else "bilinmeyen"
            satir.append(f"   ❌ {detay['segment_name']} (skor {detay['score']:.0f}%): eksik {eksik}")
        else:
            satir.append(f"   ✅ {detay['segment_name']} (skor {detay['score']:.0f}%) — uygun")

    return "\n".join(satir)


# ---------------------------------------------------------------------------
# Kolaylık fonksiyonlar
# ---------------------------------------------------------------------------

def segment_eligibility_skoru(company: dict[str, Any], segments: list[dict[str, Any]]) -> float:
    return aggregate_eligibility(company, segments)["genel_skor"]


def segment_onay_durumu(company: dict[str, Any], segments: list[dict[str, Any]]) -> str:
    return aggregate_eligibility(company, segments)["onay_durumu"]
# ---------------------------------------------------------------------------
# PO-BACK-02: Ek fonksiyonlar (eligibility_skoru, onay_durumu)
# ---------------------------------------------------------------------------

def eligibility_skoru(firma: dict[str, Any]) -> float:
    """
    Bir firmanın sektör eşleşmesi, çalışan sayısı aralığı ve veri tamlılığına göre
    0-1 aralığında bir uygunluk skoru hesaplar.

    Args:
        firma: Şirket bilgilerini içeren dict

    Returns:
        0.0 ile 1.0 arasında bir float değer
    """
    if not firma or not isinstance(firma, dict):
        return 0.0

    # Veri tamlılığı kontrolü (en az company_name ve sektör olmalı)
    if not firma.get("company_name") or not firma.get("sektor"):
        return 0.0

    # Sektör eşleşmesi skoru (0-0.33)
    sektor_puani = 0.33 if _alan_bul(firma, SEKTOR_ALANLARI) else 0.0

    # Çalışan sayısı aralığı kontrolü (0-0.33)
    # min_hacim veya revenue alanlarından çalışan sayısı tahmini yapalım
    revenue = _sayi_degeri(_alan_bul(firma, HACIM_ALANLARI))
    # Basit tahmin: revenue/10000 = çalışan sayısı (gerçekçi değil ama örnek için)
    estimated_employees = revenue / 10000 if revenue is not None else 0
    # 10-5000 çalışan arası ideal
    if 10 <= estimated_employees <= 5000:
        calisan_puani = 0.33
    elif estimated_employees > 0:
        # 10 veya 5000 dışı ancak pozitif değerler için kısmi puan
        calisan_puani = min(0.33, max(0.0, (estimated_employees - 10) / (5000 - 10) * 0.33))
    else:
        calisan_puani = 0.0

    # Veri tamlılığı skoru (0-0.34) - gerekli alanların varlığı
    required_fields = ["company_name", "sektor", "firma_tipi"]
    present_count = sum(1 for field in required_fields if firma.get(field) is not None)
    veri_puani = (present_count / len(required_fields)) * 0.34

    toplam_puan = sektor_puani + calisan_puani + veri_puani
    return round(min(toplam_puan, 1.0), 4)


def onay_durumu(skor: float, esik: float = 0.6) -> str:
    """
    Skor ve esik değeri ile onay durumunu belirler.

    Args:
        skor: 0-1 aralığında bir float değer
        esik: Eşik değeri (varsayılan: 0.6)

    Returns:
        'otomatik' (skor >= esik),
        'manuel' (0.4 <= skor < esik),
        'red' (skor < 0.4)
    """
    if skor is None or not isinstance(skor, (int, float)):
        return "red"

    skor = float(skor)
    if skor < 0 or skor > 1:
        # Geçersiz aralık, 0-1'e klipla
        skor = max(0.0, min(1.0, skor))

    if skor >= esik:
        return "otomatik"
    elif skor >= 0.4:
        return "manuel"
    else:
        return "red"