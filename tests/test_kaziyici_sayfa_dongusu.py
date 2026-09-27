# -*- coding: utf-8 -*-
"""BaseOsfbScraper.sayfa_dongusu() koruma testleri (D-235 / VERI-KAZIYICI-DONGU-01).

Gercek olay: Ivedik OSB kaziyicisi 15 firmayi 224 kez tekrar yazdi (3375 satir,
14 tekil unvan). Kok neden: WordPress gecersiz /page/N/ icin sayfa 1'i donuyor,
kod "liste bosalinca dur" bekliyordu -> sonsuz dongu.
"""
from __future__ import annotations

import logging

import pytest

from company_master.etl.scrapers.base_osfb_scraper import BaseOsfbFirma, BaseOsfbScraper


class _Sahte(BaseOsfbScraper):
    """Her sayfada AYNI listeyi donduren site (Ivedik davranisi)."""

    RATE_LIMIT_SECONDS = 0.0
    log = logging.getLogger("test")

    def __init__(self, sayfalar):
        self._sayfalar = sayfalar
        self.cagri = 0

    def fetch_firma_liste(self, page: int = 1):
        self.cagri += 1
        idx = page - 1
        if idx >= len(self._sayfalar):
            idx = 0  # site tavani asan istekte SAYFA 1'i tekrar doner (Ivedik)
        return [BaseOsfbFirma(unvan=u) for u in self._sayfalar[idx]]


def _liste(*adlar):
    return [BaseOsfbFirma(unvan=a) for a in adlar]


def test_tekrar_eden_sayfa_donguyu_durdurur():
    """Ivedik senaryosu: her sayfa ayni -> 3375 degil 15 kayit."""
    s = _Sahte([["A", "B", "C"]])
    cikti = [f.unvan for _, fs in s.sayfa_dongusu() for f in fs]
    assert cikti == ["A", "B", "C"], f"kopya sizdi: {cikti}"
    assert s.cagri < 10, f"dongu gec durdu: {s.cagri} istek"


def test_normal_sayfalama_tum_sayfalari_gezer():
    s = _Sahte([["A", "B"], ["C", "D"], ["E"]])
    cikti = [f.unvan for _, fs in s.sayfa_dongusu() for f in fs]
    assert cikti == ["A", "B", "C", "D", "E"]


def test_kismi_ortusen_sayfada_yalniz_yeniler_gelir():
    """Sayfa kaymasi (yeni kayit eklenince) ayni firmayi iki kez vermemeli."""
    s = _Sahte([["A", "B"], ["B", "C"], ["C", "D"]])
    cikti = [f.unvan for _, fs in s.sayfa_dongusu() for f in fs]
    assert cikti == ["A", "B", "C", "D"], cikti
    assert len(cikti) == len(set(cikti)), "tekil olmayan cikti"


def test_bos_sayfa_durdurur():
    class _Bos(_Sahte):
        def fetch_firma_liste(self, page: int = 1):
            self.cagri += 1
            return _liste("A") if page == 1 else []

    s = _Bos([["A"]])
    cikti = [f.unvan for _, fs in s.sayfa_dongusu() for f in fs]
    assert cikti == ["A"]


def test_max_sayfa_tavani_sonsuzlugu_keser():
    """Her sayfa FARKLI olsa bile tavan var (kotu senaryo sigortasi)."""

    class _Sonsuz(_Sahte):
        def fetch_firma_liste(self, page: int = 1):
            self.cagri += 1
            return _liste(f"firma-{page}")

    s = _Sonsuz([[]])
    s.MAX_SAYFA = 7
    cikti = [f.unvan for _, fs in s.sayfa_dongusu() for f in fs]
    assert len(cikti) == 7, cikti
    assert s.cagri == 7


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
