"""Matcher (VKN + fuzzy + vektor) birim testleri — 9R-02.

Izolasyon kurali: gercek pano/veri/9Router'a dokunmaz. rapidfuzz kurulu
olmasa bile deterministik calismasi icin fake fuzz enjekte edilir ve sonra
monkeypatch ile geri yuklenir.
"""
import pytest

from src.company_master.entity_resolution import matcher


class FakeFuzz:
    """Deterministik unvan puani: temiz unvanlar esitse 100, degilse 50."""

    def token_sort_ratio(self, a: str, b: str) -> float:
        if a == b:
            return 100.0
        return 50.0


@pytest.fixture(autouse=True)
def _fuzzy_on(monkeypatch):
    """Testleri rapidfuzz kurulumundan bagimsiz yapar."""
    monkeypatch.setattr(matcher, "HAZ_RAPIDFUZZ", True)
    monkeypatch.setattr(matcher, "fuzz", FakeFuzz())


# Kayit ornekleri: A/B ayni VKN + ayni temiz unvan (Ankara Metal),
# C farkli VKN + farkli unvan (Bursa Plastik).
A = {"vkn": "1234567890", "legal_name": "Ankara Metal Sanayi ve Ticaret A.Ş."}
B = {"vkn": "1234567890", "legal_name": "Ankara Metal Sanayi Ticaret Ltd. Şti."}
C = {"vkn": "9999999999", "legal_name": "Bursa Plastik A.Ş."}


def test_vkn_ayni_vektor_yuksek_matched():
    """Ayni VKN + vektor >= 0.62 -> matched (hybrid)."""
    r = matcher.match(A, A, vector_score=0.9)
    assert r.decision == "matched"
    assert r.method == "hybrid"
    assert r.score == 0.9


def test_vkn_ayni_vektor_orta_possible():
    """Ayni VKN + vektor 0.45-0.62 -> possible_match (vkn_exact)."""
    r = matcher.match(A, A, vector_score=0.5)
    assert r.decision == "possible_match"
    assert r.method == "vkn_exact"
    assert r.score == 0.65


def test_vkn_ayni_vektor_dusuk_unvan_iyi_matched():
    """Ayni VKN + dusuk vektor ama unvan fuzzy 80+ -> matched (vkn_exact)."""
    r = matcher.match(A, B, vector_score=0.2)
    assert r.decision == "matched"
    assert r.method == "vkn_exact"
    assert r.score == 0.8


def test_vkn_ayni_vektorsuz_unvan_iyi_matched():
    """Vektor skoru yok, ayni VKN + unvan iyi -> matched (vkn_exact)."""
    r = matcher.match(A, B)
    assert r.decision == "matched"
    assert r.method == "vkn_exact"


def test_vkn_ayni_unvan_dusuk_possible():
    """Ayni VKN, unvan dusuk -> possible_match, skor unvandan turetilir."""
    farkli_unvan = {"vkn": "1234567890", "legal_name": "Farkli Sektor A.Ş."}
    r = matcher.match(A, farkli_unvan)
    assert r.decision == "possible_match"
    assert r.method == "vkn_exact"
    assert r.score == max(0.3, 50 / 100.0)


def test_vkn_farkli_unvan_iyi_possible():
    """Farkli VKN + unvan fuzzy 80+ -> possible_match (name_fuzzy)."""
    a = dict(A, vkn="111")
    b = dict(B, vkn="222")
    r = matcher.match(a, b, vector_score=0.1)
    assert r.decision == "possible_match"
    assert r.method == "name_fuzzy"
    assert r.score == 0.75


def test_vkn_farkli_unvan_dusuk_vektor_yuksek():
    """Farkli VKN + dusuk unvan + vektor >= 0.62 -> possible_match (hybrid)."""
    r = matcher.match(A, C, vector_score=0.7)
    assert r.decision == "possible_match"
    assert r.method == "hybrid"
    assert r.score == 0.7


def test_hersey_dusuk_new_company():
    """Farkli VKN + dusuk unvan + vektor yok -> new_company (manual)."""
    r = matcher.match(A, C)
    assert r.decision == "new_company"
    assert r.method == "manual"
    assert r.score == 0.0


def test_vkn_bos_noktalama_ignored():
    """Bos/N/A VKN degerleri kiyaslamada yok sayilir."""
    bos_vkn = {"vkn": "-", "legal_name": "Ankara Metal A.Ş."}
    r = matcher.match(A, bos_vkn, vector_score=0.9)
    # vkn esit sayilmaz; unvan iyi + vektor yuksek -> hybrid
    assert r.decision == "possible_match"
    assert r.method in ("name_fuzzy", "hybrid")


def test_match_semantic_vektor_zorunlu():
    """match_semantic vector_score zorunludur; ayni VKN + yuksek -> matched."""
    r = matcher.match_semantic(A, A, vector_score=0.85)
    assert r.decision == "matched"
    assert r.method == "hybrid"


def test_temiz_unvan_onemsiz_ekleri_elenir():
    """'sanayi' ve 'ticaret' ekleri temiz unvandan duser."""
    s = matcher._temiz_unvan("Ankara Metal Sanayi ve Ticaret A.Ş.")
    assert "sanayi" not in s
    assert "ticaret" not in s
    assert s.startswith("ankara metal")


def test_temiz_unvan_bos_girdi():
    assert matcher._temiz_unvan("") == ""
    assert matcher._temiz_unvan(None) == ""


def test_esiklar_raporu():
    e = matcher.esiklar()
    assert e["vkn_eslesme"] == 0.85
    assert e["fuzzy_eslesme"] == 80
    assert e["vektor_eslesme"] == 0.62
    assert e["vektor_possible"] == 0.45


def test_matchresult_to_dict():
    r = matcher.MatchResult(score=0.8999999, decision="matched", method="hybrid")
    d = r.to_dict()
    assert d["score"] == round(0.8999999, 6)
    assert d["decision"] == "matched"
    assert d["method"] == "hybrid"
