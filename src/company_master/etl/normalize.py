"""NORMALIZATION adimi: source_records -> companies.

Idempotent: yalnizca companies.source_record_id NULL olan kayitlari isler.
Her kayit bir kez companies''e tasinir; yeniden calistirma tekrar eklemez.

ANA KURAL (V10/09_kurallar_ve_promptlar/11_unvan_kisaltma_ve_tabela_kurallari):
  - Kural 1: Firma adlari (legal_name) her zaman BUYUK HARFLE yazilir.
  - Kural 2: Uzun ifadeler standart kisaltilir (SANAYI VE TICARET -> SAN. VE TIC.)
  - Kural 3: Tabela ismi (trade_name) = marka/ilgi alani (ilk 2-3 kelime,
    sirket turu/faaliyet kisaltilari ve "VE" blogunu gecer)

Kullanim:
    python -m company_master.etl.normalize [--only N]
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List

from sqlalchemy import text

from ..db.connection import get_engine


# ── ANA KURAL: Firma ad normalizasyonu (ingest-time) ──
# Kural 1: Firma adlari her zaman BUYUK HARFLE yazilir
# Kural 2: Uzun ifadeler standart kisaltilir
# Kural 3: Tabela ismi = ilgi alani/marka (ilk 2-3 kelime, VE/Şirket Tur/ Faaliyet filtrelenerek)

_COMPANY_TYPE_ABBR = {
    'ANONIM SIRKETI': 'A.S.', 'ANONIM SIRKET': 'A.S.', 'ANONIM ORTAKLIK': 'A.S.',
    'ANONIM ORTAKLIGI': 'A.S.', 'LIMITED SIRKETI': 'LTD. STI.', 'LIMITED SIRKET': 'LTD. STI.',
    'LTD. SIRKETI': 'LTD. STI.', 'LTD. SIRKET': 'LTD. STI.', 'LIMITED': 'LTD. STI.',
    'LTD': 'LTD. STI.', 'KOLLEKTIF SIRKETI': 'KOL. STI.', 'KOLLEKTIF SIRKET': 'KOL. STI.',
    'KOMANDIT SIRKETI': 'KOM. STI.', 'KOMANDIT SIRKET': 'KOM. STI.',
    'ORTAKLIK': 'ORT.', 'ORTAKLIGI': 'ORT.', 'ADI ORTAKLIK': 'ORT.', 'ADI ORTAKLIGI': 'ORT.',
    'TURK ANONIM SIRKETI': 'TAS', 'TURK ANONIM ORTAKLIK': 'TAS', 'KOOPERATIF': 'KOOP.',
}

_ACTIVITY_ABBR = {
    'SANAYI': 'SAN.', 'SANAYII': 'SAN.', 'TICARET': 'TIC.', 'TICARETI': 'TIC.',
    'PAZARLAMA': 'PAZ.', 'ITHALAT': 'ITH.', 'IHRACAT': 'IHR.',
    'MUHENDISLIK': 'MUH.', 'MUHENDIS': 'MUH.', 'MIMARLIK': 'MIM.', 'MIMAR': 'MIM.',
    'INSANAT': 'INS.', 'INSAA': 'INS.', 'NAKLIYAT': 'NAK.', 'NAKLIYE': 'NAK.',
    'TASICILIK': 'NAK.', 'OTOMOTIV': 'OTO.', 'OTOMOBIL': 'OTO.', 'TURIZM': 'TUR.',
    'TEKSTIL': 'TEK.', 'GIDA': 'GIDA', 'HIZMET': 'HIZM.', 'HIZMETLERI': 'HIZM.',
    'TARIM': 'TAR.', 'TARIMSAL': 'TAR.', 'MADENCILIK': 'MAD.', 'MADEN': 'MAD.',
    'IMALAT': 'IMAL.', 'BILISIM': 'BIL.', 'BILGISAYAN': 'BIL.', 'YAZILIM': 'YAZ.',
    'MAKINE': 'MAK.', 'MAKINA': 'MAK.', 'MOBILYA': 'MOB.',
    'ELEKTRIK': 'ELEK.', 'ELEKTRONIK': 'ELEK.', 'KIMYA': 'KIM.', 'KIMYAVI': 'KIM.',
}

_COMBO_ABBR = {
    'SANAYI VE TICARET': 'SAN. VE TIC.', 'SANAYII VE TICARETI': 'SAN. VE TIC.',
    'TICARET VE SANAYI': 'TIC. VE SAN.', 'TICARETI VE SANAYII': 'TIC. VE SAN.',
    'ITHALAT VE IHRACAT': 'ITH. IHR.', 'IHRACAT VE ITHALAT': 'IHR. ITH.',
    'INSANAT SANAYI VE TICARET': 'INS. SAN. TIC.',
    'MUHENDISLIK MIMARLIK': 'MUH. MIM.', 'TURIZM VE TICARET': 'TUR. TIC.',
    'GIDA SANAYI VE TICARET': 'GIDA SAN. TIC.',
    'TEKSTIL SANAYI VE TICARET': 'TEK. SAN. TIC.',
    'NAKLIYAT VE TICARET': 'NAK. TIC.',
}

_TRADE_NAME_STOP_WORDS = frozenset({
    'VE', 'ILE', 'BI', 'AMMA', 'LAKIK',
    'SAN.', 'SANAYI', 'SANAYII', 'TIC.', 'TICARET', 'TICARETI',
    'LTD. STI.', 'LTD. STI', 'LTD.', 'LTD', 'A.S.', 'A.S', 'A.Ş.', 'A.Ş',
    'STI.', 'STI', 'ORT.', 'ORT', 'KOL. STI.', 'KOM. STI.', 'KOOP.',
    'PAZ.', 'ITH.', 'IHR.', 'MUH.', 'MIM.', 'INS.', 'NAK.', 'OTO.',
    'TUR.', 'TEK.', 'GIDA', 'HIZM.', 'TAR.', 'MAD.', 'IMAL.',
    'BIL.', 'YAZ.', 'MAK.', 'MOB.', 'ELEK.', 'KIM.',
    'KOOP', 'Tas', 'TAO', 'DTM', 'KOBI',
})


def normalize_company_name(name: str) -> str:
    """Firma adini BUYUK HARFE cevirir ve standart kisaltilari uygular.

    Kural 1+2. Cikti web_app.py ile AYNI olmalidir (Turkce kisaltmalar:
    TIC.->TİC., STI.->ŞTİ., MUH.->MÜH.; Y9 regresyon sabitleri). Bu yuzden
    kanonik web_app.normalize_company_name'e delege edilir; import olmazsa
    ASCII yerel sozluk (_normalize_company_name_ascii) yalnizca acil durum
    gecisidir.
    """
    if not name:
        return ""
    try:
        import web_app  # proje kokunde (sys.path) — kanonik kurallar
        return web_app.normalize_company_name(name)
    except Exception:
        return _normalize_company_name_ascii(name)


def _normalize_company_name_ascii(name: str) -> str:
    """Yedek: eski ASCII sozluk (web_app import edilemezse)."""
    name = str(name).upper().strip()
    name = re.sub(r'\s{2,}', ' ', name)
    for long_phrase, short_form in sorted(_COMBO_ABBR.items(), key=lambda x: -len(x[0])):
        name = name.replace(long_phrase, short_form)
    for long_phrase, short_form in sorted(_ACTIVITY_ABBR.items(), key=lambda x: -len(x[0])):
        name = re.sub(r'\b' + re.escape(long_phrase) + r'\b', short_form, name)
    for long_phrase, short_form in sorted(_COMPANY_TYPE_ABBR.items(), key=lambda x: -len(x[0])):
        name = re.sub(r'\b' + re.escape(long_phrase) + r'\b', short_form, name)
    return re.sub(r'\s{2,}', ' ', name).strip()

def extract_trade_name(legal_name: str) -> str:
    """Uzun sirket adindan tabela ismini cikarir (web_app ile ayni kural)."""
    if not legal_name:
        return ""
    try:
        import web_app
        return web_app.extract_trade_name(legal_name)
    except Exception:
        return _extract_trade_name_ascii(legal_name)


def _extract_trade_name_ascii(legal_name: str) -> str:
    """Yedek: eski ASCII sozluk (web_app import edilemezse)."""
    normalized = _normalize_company_name_ascii(legal_name)
    words = re.split(r'[\s.]+', normalized)
    filtered = [w for w in words if w and w not in _TRADE_NAME_STOP_WORDS and len(w) > 1]
    if not filtered:
        filtered = [w for w in words if w and w not in ('VE', 'ILE')]
    return ' '.join(filtered[:3])

@dataclass
class NormalizeResult:
    total: int = 0
    written: int = 0
    errors: List[str] = field(default_factory=list)


# Kritik alan agirliklari (toplam = 100; cezalar ayrica)
CRITICAL_FIELDS = {
    "adres": 20,
    "web_sitesi": 15,
    "vergi_no": 20,
    "osb_parsel": 15,
    "sektor": 10,
    "nace_code": 5,
    "telefon": 10,
    "email": 5,
}

CRITICAL_PENALTIES = {
    "adres": 10,
    "vergi_no": 15,
    "web_sitesi": 5,
}


def _has(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0
    return True


def _data_quality_score(row: Dict[str, Any]) -> float:
    """Veri kalite skoru (0-100).

    - Kritik alanlar: adres (20), vergi_no (20), web_sitesi (15), osb_parsel (15),
      sektor (10), nace_code (5), telefon (10), email (5) -> toplam 100
    - Bos kritik alanlara ek ceza: vergi_no (-15), adres (-10), web_sitesi (-5)
    - Tum telefon/email/vergi_no birlikte bossa ekstra -5
    """
    payload = row.get("raw_payload") or {}
    skor = 0.0

    if _has(row.get("raw_phone")):
        skor += CRITICAL_FIELDS["telefon"]
    if _has(row.get("raw_email")):
        skor += CRITICAL_FIELDS["email"]
    if _has(row.get("raw_website")):
        skor += CRITICAL_FIELDS["web_sitesi"]
    elif _has(row.get("website_domain")):
        skor += CRITICAL_FIELDS["web_sitesi"]
    if _has(payload.get("adres")):
        skor += CRITICAL_FIELDS["adres"]
    if _has(payload.get("sektor")):
        skor += CRITICAL_FIELDS["sektor"]
    if _has(row.get("raw_tax_number")):
        skor += CRITICAL_FIELDS["vergi_no"]
    if _has(payload.get("osb_parsel")):
        skor += CRITICAL_FIELDS["osb_parsel"]
    if _has(payload.get("nace_code")):
        skor += CRITICAL_FIELDS["nace_code"]

    if not _has(row.get("raw_tax_number")) and not _has(payload.get("vergi_no")):
        skor -= CRITICAL_PENALTIES["vergi_no"]
    if not _has(payload.get("adres")):
        skor -= CRITICAL_PENALTIES["adres"]
    if not _has(row.get("raw_website")) and not _has(row.get("website_domain")):
        skor -= CRITICAL_PENALTIES["web_sitesi"]

    if not _has(row.get("raw_phone")) and not _has(row.get("raw_email")) and not _has(row.get("raw_tax_number")):
        skor -= 5

    return min(max(skor, 0.0), 100.0)


def _map_row(row: Dict[str, Any], osb_id: str | None) -> Dict[str, Any]:
    """source_records satirini companies satirina esler.

    ANA KURAL uygulanir:
      - legal_name -> BUYUK HARF
      - trade_name -> ilk 2 KELIME (hece degil)
    """
    payload = row.get("raw_payload") or {}
    phones = [p for p in (row.get("raw_phone") or "").split("; ") if p]
    emails = [e for e in (row.get("raw_email") or "").split("; ") if e]
    nace_conf = payload.get("nace_confidence", "low")
    nace_validity = "high" if nace_conf == "high" else "medium" if nace_conf == "medium" else "unknown"
    # ANA KURAL: legal_name BUYUK HARF, trade_name ilk 2 kelime
    legal_name = normalize_company_name(row["raw_name"])
    trade_name = extract_trade_name(legal_name)
    return {
        "source_record_id": row["source_record_id"],
        "legal_name": legal_name,
        "trade_name": trade_name,
        "company_type": None,
        "tax_number": row.get("raw_tax_number"),
        "website_domain": row.get("raw_website"),
        "primary_phone": phones[0] if phones else None,
        "primary_email": emails[0] if emails else None,
        "osb_id": osb_id,
        "is_osb_member": True,
        "is_ankara": True,
        "status": "active",
        "nace_validity": nace_validity,
        "data_quality_score": _data_quality_score(row),
        "entity_confidence": 0.9,
    }


def run_normalize(limit: int | None = None) -> NormalizeResult:
    res = NormalizeResult()
    engine = get_engine()

    with engine.begin() as conn:
        osb = conn.execute(
            text("SELECT osb_id FROM osbs WHERE name = :n"), {"n": "OSTIM OSB"}
        ).first()
        osb_id = str(osb[0]) if osb else None

        rows = conn.execute(
            text("""
                SELECT sr.source_record_id, sr.raw_name, sr.raw_phone, sr.raw_email,
                       sr.raw_website, sr.raw_tax_number, sr.raw_payload
                FROM source_records sr
                LEFT JOIN companies c ON c.source_record_id = sr.source_record_id
                WHERE c.company_id IS NULL
                ORDER BY sr.collected_at
            """)
        ).mappings().all()
        if limit:
            rows = rows[:limit]

        res.total = len(rows)
        if not rows:
            return res

        batch = [_map_row(dict(r), osb_id) for r in rows]

        conn.execute(
            text("""
                INSERT INTO companies
                (legal_name, trade_name, company_type, tax_number, website_domain,
                 primary_phone, primary_email, osb_id, is_osb_member, is_ankara,
                 status, nace_validity, data_quality_score, entity_confidence,
                 source_record_id, last_verified_at)
                VALUES
                (:legal_name, :trade_name, :company_type, :tax_number, :website_domain,
                 :primary_phone, :primary_email, :osb_id, :is_osb_member, :is_ankara,
                 :status, :nace_validity, :data_quality_score, :entity_confidence,
                 :source_record_id, NOW())
            """),
            batch,
        )
        res.written = len(batch)
    return res


def main() -> int:
    parser = argparse.ArgumentParser(description="Company Master normalize")
    parser.add_argument("--only", type=int, default=None, help="Ilk N kaydi isle (test)")
    args = parser.parse_args()

    res = run_normalize(args.only)
    print(f"Toplam: {res.total}")
    print(f"Yazilan: {res.written}")
    for e in res.errors:
        print(f"HATA: {e}")
    return 0 if not res.errors else 1


if __name__ == "__main__":
    sys.exit(main())