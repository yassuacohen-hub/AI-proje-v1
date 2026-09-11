"""Şirket eşleştirme motoru (9R-02 dolduruldu).

VKN exact + unvan fuzzy (rapidfuzz) + vektör benzerliği (9Router) üçlüsüyle
iki firma kaydı arasında eşleşme kararı verir. V9 8.3 Global Deduplication
referansi: ayni VKN'li kayitlar semantik skorla ayrilir.

Kullanim:
    match(record_a, record_b) -> MatchResult(score, decision, method)
Yalnizca vektor modu icin:
    match_semantic(record_a, record_b, vector_scores)  # vektör skoru dışarıdan
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MatchResult:
    """İki şirket kaydı arasındaki eşleşme sonucu."""
    score: float
    decision: str  # matched / possible_match / new_company / rejected
    method: str    # vkn_exact / name_fuzzy / hybrid / manual

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": round(self.score, 6),
            "decision": self.decision,
            "method": self.method,
        }


try:
    from rapidfuzz import fuzz  # type: ignore
    HAZ_RAPIDFUZZ = True
except ImportError:  # pragma: no cover
    fuzz = None  # type: ignore[assignment]
    HAZ_RAPIDFUZZ = False

# Esik degerleri (baslangic; kalibrasyon ileride)
TH_VKN_ESLESME = 0.85      # ayni VKN + yuksek sematik -> matched
TH_FUZZ_ESLESME = 80       # unvan benzerlik puani (0-100)
TH_VEKTOR_ESLESME = 0.62   # vektor/cosine benzerligi (0-1)
TH_VEKTOR_POSSIBLE = 0.45

# Onemsiz unvan takilari (unvan karsilastirmasinda elenir)
_ONEMSIZ = ("anonim", "şirketi", "şirket", "limited", "ltd", "şti", "sanayi",
            "ticaret", "trade", "industrial", "inc", "corp", "corp.", "holding")


def _temiz_unvan(unvan: str) -> str:
    """Unvani normalize eder: kucuk harf, noktalamalar, onemsiz takilar."""
    import re
    if not unvan:
        return ""
    s = unvan.lower()
    s = re.sub(r"[^a-zçğıöşü0-9 ]", " ", s)
    parcalar = [p for p in s.split() if p and p not in _ONEMSIZ]
    return " ".join(parcalar)


def _vkn_benzer(ra: dict, rb: dict, vkn_key: str = "vkn") -> tuple[bool, str]:
    """VKN'lari ayni mi? (bos/N/A ignoring)."""
    va = str(ra.get(vkn_key) or "").strip()
    vb = str(rb.get(vkn_key) or "").strip()
    if not va or not vb or va.lower() in ("-", "none", "n/a", "yok"):
        return False, ""
    return va == vb, va


def _unvan_puan(ra: dict, rb: dict) -> float:
    """Unvan fuzzy benzerlik puani (0-100); zorunlu alan yoksa 0."""
    if not HAZ_RAPIDFUZZ:
        return 0.0
    a = _temiz_unvan(str(ra.get("legal_name") or ra.get("unvan") or ""))
    b = _temiz_unvan(str(rb.get("legal_name") or rb.get("unvan") or ""))
    if not a or not b:
        return 0.0
    return float(fuzz.token_sort_ratio(a, b))


def match(record_a: dict, record_b: dict,
          vector_score: float | None = None) -> MatchResult:
    """İki kayıt arasında eşleşme skoru hesaplar.

    Karar mantigi:
      1. VKN ayni + vektor yuksek (>TH_VEKTOR_ESLESME) -> matched (hybrid)
      2. VKN ayni + vektor orta/dusuk                 -> possible_match (vkn_exact)
      3. VKN farkli + unvan fuzzy 80+                  -> possible_match (name_fuzzy)
      4. Vektör yuksek (>0.62) + unvan orta            -> possible_match (hybrid)
      5. diger -> new_company
    """
    vkn_ayni, vkn = _vkn_benzer(record_a, record_b)
    unvan_p = _unvan_puan(record_a, record_b)

    if vkn_ayni:
        # ayni VKN'li iki kayit: vektor skoru icin embed gerekli
        if vector_score is not None:
            if vector_score >= TH_VEKTOR_ESLESME:
                return MatchResult(score=0.9, decision="matched", method="hybrid")
            if vector_score >= TH_VEKTOR_POSSIBLE:
                return MatchResult(score=0.65, decision="possible_match", method="vkn_exact")
        # vektor yok: unvana guveniriz
        if unvan_p >= TH_FUZZ_ESLESME:
            return MatchResult(score=0.8, decision="matched", method="vkn_exact")
        return MatchResult(
            score=max(0.3, unvan_p / 100.0),
            decision="possible_match",
            method="vkn_exact",
        )

    # VKN farkli/eksik -> unvan + vektor
    if unvan_p >= TH_FUZZ_ESLESME:
        return MatchResult(score=0.75, decision="possible_match", method="name_fuzzy")
    if vector_score is not None and vector_score >= TH_VEKTOR_ESLESME:
        return MatchResult(score=0.7, decision="possible_match", method="hybrid")
    return MatchResult(score=0.0, decision="new_company", method="manual")


def match_semantic(record_a: dict, record_b: dict,
                   vector_score: float) -> MatchResult:
    """Vektör skoru zorunlu olan sürüm (matcher vektörsüz de çalışır)."""
    return match(record_a, record_b, vector_score=vector_score)


def esiklar() -> dict[str, float]:
    """Mevcut eşik değerlerini döner (kalibrasyon/report için)."""
    return {
        "vkn_eslesme": TH_VKN_ESLESME,
        "fuzzy_eslesme": TH_FUZZ_ESLESME,
        "vektor_eslesme": TH_VEKTOR_ESLESME,
        "vektor_possible": TH_VEKTOR_POSSIBLE,
    }
