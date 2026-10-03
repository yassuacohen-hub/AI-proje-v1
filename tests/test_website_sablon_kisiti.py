# -*- coding: utf-8 -*-
"""Mandal: goc 0052 trigger deseni == yazma_kapisi.SABLON_WEB_DESEN (D-211/D-233).

SQL'de desen iki yerde gecer (trigger + tek seferlik UPDATE); ikisi de Python
kapisiyla BIREBIR ayni dizgi olmali. Liste degisirse once yazma_kapisi.py,
sonra yeni goc; bu test eski goc dosyasinin sessizce sapmasini engeller.
Kirilarak dogrulandi (D-256/4): SQL'den bir alan silinince FAIL.

Ilgili Nodlar: [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]] ·
[[Huginn Data Insights/docs/BORC_DEFTERI]] (BORC-SITE-COP-01) ·
[[Huginn Data Insights/src/company_master/schema/migrations/0052_website_sablon_kisiti.sql]] ·
[[Huginn Data Insights/src/company_master/db/yazma_kapisi.py]]
"""
from __future__ import annotations

import re
from pathlib import Path

from company_master.db.yazma_kapisi import SABLON_WEB_DESEN, sablon_mu

KOK = Path(__file__).resolve().parents[1]
GOC = KOK / "src/company_master/schema/migrations/0052_website_sablon_kisiti.sql"
RE_DESEN = re.compile(r"~\s*\n?\s*'([^']+)'")


def _sql_desenleri() -> list[str]:
    return RE_DESEN.findall(GOC.read_text(encoding="utf-8"))


def test_goc_deseni_python_kapisiyla_esit() -> None:
    desenler = _sql_desenleri()
    assert len(desenler) == 2, desenler  # trigger + UPDATE
    for d in desenler:
        assert d == SABLON_WEB_DESEN, (d, SABLON_WEB_DESEN)


def test_desen_alan_sinirinda() -> None:
    """Olculen 4 gercek alan (2026-10-04) sablon sayilmaz; sablonlar sayilir."""
    for gercek in ("https://enerjilastik.wixsite.com", "https://www.epsiloncomposite.com/",
                   "https://www.aerocomposite.com.tr"):
        assert not sablon_mu(gercek), gercek
    for sablon in ("http://www.isim.org.tr", "x.osp.com.tr", "ostimonline.com/home",
                   "www.ostimistihdam.com", "site.com"):
        assert sablon_mu(sablon), sablon
