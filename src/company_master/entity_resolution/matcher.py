"""Şirket eşleştirme motoru (iskelet)."""

from dataclasses import dataclass


@dataclass
class MatchResult:
    """İki şirket kaydı arasındaki eşleşme sonucu."""
    score: float
    decision: str  # matched / possible_match / new_company / rejected
    method: str    # vkn_exact / name_fuzzy / manual


def match(record_a: dict, record_b: dict) -> MatchResult:
    """İki kayıt arasında eşleşme skoru hesaplar (iskelet)."""
    raise NotImplementedError("match henüz implemente edilmedi.")
