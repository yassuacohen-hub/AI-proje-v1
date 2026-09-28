# -*- coding: utf-8 -*-
"""D-250 TEK KAPI: kimlik tamligi puani (identity_completeness, 0-10).

Puan ureten baska yol yoktur. Bir alan puan alabilmek icin:
  1. Dolu olacak (bos dize dolu sayilmaz),
  2. D-246 kapisindan (kimlik_no.py) gecen bir kimlik ise dogrulanmis olacak,
  3. D-245 geregi kanit olacak; tahmin/varsayilan puan almaz.

Agirlik seti degisirse SURUM artar ve eski puanlar BAYAT sayilir (D-250/4).
"""
from __future__ import annotations

from sqlalchemy import text

from ..db.connection import get_engine
from .kimlik_no import kimlik_dogrula, mersis_dogrula, sicil_dogrula

__all__ = [
    "SURUM",
    "AGIRLIKLAR",
    "identity_completeness",
    "alan_puanlari",
    "bayat_mi",
    "recalc_quality_scores",
]

SURUM = "v1"

# D-250 agirlik seti v1 — toplam tam 10.0.
# Kimlik omurgasi 6.0 + Erisim 4.0.
AGIRLIKLAR: dict[str, float] = {
    "legal_name": 1.0,              # ticaret unvani
    "tax_number": 1.5,              # D-250/3: kaynak baglaninca 3.0 -> v2
    "tax_office": 0.5,
    "mersis_number": 1.0,
    "trade_registry_number": 1.0,   # sicil no + dairesi birlikte
    "nace_code": 1.0,
    "address": 1.5,
    "primary_phone": 1.5,
    "primary_email": 0.7,
    "website_domain": 0.3,
}

# D-245: kanit sayilan NACE kaynaklari. Tahmin/varsayilan puan almaz.
NACE_KANIT_KAYNAKLARI = frozenset({"mersis", "external"})


def _dolu(v) -> bool:
    return bool(v) and bool(str(v).strip())


def alan_puanlari(row: dict) -> dict[str, float]:
    """Her alanin kazandigi puan. Kazanilmayan alan 0.0 dondurur (D-249/3:
    "veri yok" kolonda NULL kalir, puana katkisi 0'dir)."""
    p = dict.fromkeys(AGIRLIKLAR, 0.0)

    if _dolu(row.get("legal_name")):
        p["legal_name"] = AGIRLIKLAR["legal_name"]

    # D-246 kapisi: dogrulanmayan VKN/TCKN puan almaz.
    # kimlik_dogrula -> (deger, tur); tur "vkn"/"tckn"/"gecersiz".
    _deger, _tur = kimlik_dogrula(row.get("tax_number"))
    if _deger and _tur in ("vkn", "tckn"):
        p["tax_number"] = AGIRLIKLAR["tax_number"]

    if _dolu(row.get("tax_office")):
        p["tax_office"] = AGIRLIKLAR["tax_office"]

    if mersis_dogrula(row.get("mersis_number"))[0]:
        p["mersis_number"] = AGIRLIKLAR["mersis_number"]

    # D-250: sicil no TEK BASINA yetmez, dairesi de gerekir.
    if sicil_dogrula(row.get("trade_registry_number"))[0] and _dolu(
        row.get("trade_registry_office")
    ):
        p["trade_registry_number"] = AGIRLIKLAR["trade_registry_number"]

    # D-245: tahmin edilmis NACE kanit degildir.
    if _dolu(row.get("nace_code")) and row.get("nace_source") in NACE_KANIT_KAYNAKLARI:
        p["nace_code"] = AGIRLIKLAR["nace_code"]

    for alan in ("address", "primary_phone", "primary_email", "website_domain"):
        if _dolu(row.get(alan)):
            p[alan] = AGIRLIKLAR[alan]

    return p


def identity_completeness(row: dict) -> float:
    """Kimlik tamligi puani, 0.0-10.0."""
    toplam = round(sum(alan_puanlari(row).values()), 1)
    return min(max(toplam, 0.0), 10.0)


def bayat_mi(score_version: str | None) -> bool:
    """D-250/4: baska bir agirlik setiyle hesaplanmis puan bayattir."""
    return score_version != SURUM


_SORGU = """
    SELECT company_id, legal_name, tax_number, tax_office, mersis_number,
           trade_registry_number, trade_registry_office, nace_code, nace_source,
           address, primary_phone, primary_email, website_domain
    FROM companies
"""

# D-249/2: satir basina UPDATE yasak. Tum puanlar tek ifadede yazilir.
_YAZ = """
    UPDATE companies c
       SET identity_completeness = v.s, score_version = :v
      FROM (SELECT unnest(CAST(:ids AS uuid[]))          AS cid,
                   unnest(CAST(:skorlar AS numeric[]))   AS s) v
     WHERE c.company_id = v.cid
"""


def recalc_quality_scores() -> int:
    """Tum firmalarin kimlik tamligini yeniden hesaplar ve toplu yazar."""
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text(_SORGU)).mappings().all()
        if not rows:
            return 0
        conn.execute(
            text(_YAZ),
            {
                "ids": [str(r["company_id"]) for r in rows],
                "skorlar": [identity_completeness(dict(r)) for r in rows],
                "v": SURUM,
            },
        )
    return len(rows)
