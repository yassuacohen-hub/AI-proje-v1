"""NORMALIZATION adımı: source_records → companies.

Idempotent: yalnızca `companies.source_record_id` NULL olan kayıtları işler.
Her kayıt bir kez companies'e taşınır; yeniden çalıştırma tekrar eklemez.

Kullanım:
    python -m company_master.etl.normalize [--only N]
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List

from sqlalchemy import text

from ..db.connection import get_engine


@dataclass
class NormalizeResult:
    total: int = 0
    written: int = 0
    errors: List[str] = field(default_factory=list)


def _map_row(row: Dict[str, Any], osb_id: str | None) -> Dict[str, Any]:
    """source_records satırını companies satırına eşler."""
    payload = row.get("raw_payload") or {}
    phones = [p for p in (row.get("raw_phone") or "").split("; ") if p]
    emails = [e for e in (row.get("raw_email") or "").split("; ") if e]
    nace_conf = payload.get("nace_confidence", "low")
    nace_validity = "high" if nace_conf == "high" else "medium" if nace_conf == "medium" else "unknown"
    return {
        "source_record_id": row["source_record_id"],
        "legal_name": row["raw_name"].strip(),
        "trade_name": None,
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
        "data_quality_score": 70.0 if row.get("raw_phone") else 40.0,
        "entity_confidence": 0.9,
    }


def run_normalize(limit: int | None = None) -> NormalizeResult:
    res = NormalizeResult()
    engine = get_engine()

    with engine.begin() as conn:
        osb = conn.execute(
            text("SELECT osb_id FROM osbs WHERE name = :n"), {"n": "OSTİM OSB"}
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
    parser.add_argument("--only", type=int, default=None, help="İlk N kaydı işle (test)")
    args = parser.parse_args()

    res = run_normalize(args.only)
    print(f"Toplam: {res.total}")
    print(f"Yazılan: {res.written}")
    for e in res.errors:
        print(f"HATA: {e}")
    return 0 if not res.errors else 1


if __name__ == "__main__":
    sys.exit(main())