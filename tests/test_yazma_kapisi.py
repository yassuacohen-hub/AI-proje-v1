# -*- coding: utf-8 -*-
"""D-303: veri yazma kapisi + MANDAL-SABLON-01.

Olcum (D-303): `companies`.website_domain 2666 kayitta sablon; hepsi tek
kaynaktan (ostim.org.tr / web_scrape). Kok sebep: kanonik yasak-deger listesi
yoktu, ayni liste 23 dosyada kopyalanmisti. Kopyalar birbirinden sapti.

Mandal: kopya sayisi ARTAMAZ. Yeni kod kanonik listeyi import eder, kopyalamaz.
"""
from __future__ import annotations

import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))

from company_master.db.yazma_kapisi import (  # noqa: E402
    SABLON_WEB, kabul, sablon_mu, temizle,
)

# D-303 olcumu: 23 dosya kanonik listeyi kopyaliyor. Tavan yalniz kucuulur.
TAVAN_KOPYA = 23
ATLA = {".venv", ".git", "node_modules", "__pycache__", "backups",
        "_ARSIV_tek_kullanimlik", "tests"}
IZ = ("isim.org.tr", "osp.com.tr", "ostimonline", "ostimistihdam")


def _kopyalayanlar() -> list[str]:
    bulgu = []
    for p in KOK.rglob("*.py"):
        if ATLA & set(p.parts) or p.name == "yazma_kapisi.py":
            continue
        try:
            m = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(i in m for i in IZ):
            bulgu.append(p.relative_to(KOK).as_posix())
    return sorted(bulgu)


def test_sablon_web_reddedilir() -> None:
    for d in ("http://www.isim.org.tr", "HTTPS://ISIM.ORG.TR/",
              "www.ostimonline.com/home", "x.osp.com.tr"):
        assert sablon_mu(d), d


def test_gercek_alan_adi_gecer() -> None:
    for d in ("https://gercekfirma.com.tr", "abc.net", None, ""):
        assert not sablon_mu(d), d


def test_yokluk_sifir_degil_bostur() -> None:
    """D-249: 0, '-', 'yok' bilgi degildir."""
    for d in ("0", "-", " yok ", "N/A", "null", ""):
        assert temizle(d) is None, d
    assert temizle(" Ankara ") == "Ankara"


def test_kabul_sabloni_yazmaz_ve_sebep_verir() -> None:
    temiz, sebep = kabul({"website_domain": "http://www.isim.org.tr",
                          "source_record_id": "x"})
    assert temiz["website_domain"] is None
    assert any("sablon" in s for s in sebep)


def test_kabul_kokensiz_kaydi_isaretler() -> None:
    """D-287: dogrulanmamis veri dogrulanmis gibi gecmez."""
    _, sebep = kabul({"website_domain": "https://ok.com.tr"})
    assert any("koken yok" in s for s in sebep)


def test_kabul_temiz_kaydi_bozmaz() -> None:
    temiz, sebep = kabul({"website_domain": "https://gercekfirma.com.tr",
                          "source_record_id": "x"})
    assert temiz["website_domain"] == "https://gercekfirma.com.tr"
    assert sebep == []


def test_kanonik_liste_kopyasi_artmaz() -> None:
    k = _kopyalayanlar()
    assert len(k) <= TAVAN_KOPYA, (
        f"SABLON LISTESI KOPYASI ARTTI: {len(k)} > {TAVAN_KOPYA}. "
        f"Kanonik listeyi import et: "
        f"from company_master.db.yazma_kapisi import SABLON_WEB. Kopyalar: {k}"
    )
    assert SABLON_WEB, "kanonik liste bos olamaz"
