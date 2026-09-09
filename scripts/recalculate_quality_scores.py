#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DB kalite skorlarini yeniden hesapla - duyarlı cezalar ile.

Yeni formul (2026-09-08, hedef ortalama >= 50):
  + telefon 10, email 5, web_sitesi 15, adres 20, sektor 10,
    vergi_no 20, osb_parsel 15, nace_code 5
  - vergi_no bossa -8, adres bossa -5, web_sitesi bossa -2,
    telefon+email+vergi_no ucu de bossa ekstra -2

Kullanimi:
    python scripts/recalculate_quality_scores.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text

from company_master.db.connection import get_engine


NEW_QUALITY_SQL = text("""
    UPDATE companies c
    SET data_quality_score = GREATEST(0, LEAST(100, (
        10
        + CASE WHEN COALESCE(c.primary_phone, sr.raw_phone) IS NOT NULL
                  AND COALESCE(c.primary_phone, sr.raw_phone) <> '' THEN 10 ELSE 0 END
        + CASE WHEN COALESCE(c.primary_email, sr.raw_email) IS NOT NULL
                  AND COALESCE(c.primary_email, sr.raw_email) <> '' THEN 5 ELSE 0 END
        + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NOT NULL
                  AND COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) <> '' THEN 15 ELSE 0 END
        + CASE WHEN COALESCE(c.adres, sr.raw_payload->>:adres) IS NOT NULL
                  AND COALESCE(c.adres, sr.raw_payload->>:adres) <> '' THEN 20 ELSE 0 END
        + CASE WHEN COALESCE(c.osb_parsel, sr.raw_payload->>:osb_parsel) IS NOT NULL
                  AND COALESCE(c.osb_parsel, sr.raw_payload->>:osb_parsel) <> '' THEN 15 ELSE 0 END
        + CASE WHEN sr.raw_payload->>:sektor IS NOT NULL
                  AND sr.raw_payload->>:sektor <> '' THEN 10 ELSE 0 END
        + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NOT NULL
                  AND COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) <> '' THEN 20 ELSE 0 END
        + CASE WHEN (sr.raw_payload->>:nace_code IS NOT NULL
                      AND sr.raw_payload->>:nace_code <> '')
                    OR (sr.raw_nace IS NOT NULL AND sr.raw_nace <> '') THEN 5 ELSE 0 END
        + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL
                  OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '' THEN -8 ELSE 0 END
        + CASE WHEN COALESCE(c.adres, sr.raw_payload->>:adres) IS NULL
                  OR COALESCE(c.adres, sr.raw_payload->>:adres) = '' THEN -5 ELSE 0 END
        + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NULL
                  OR COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) = '' THEN -2 ELSE 0 END
        + CASE WHEN (COALESCE(c.primary_phone, sr.raw_phone) IS NULL OR COALESCE(c.primary_phone, sr.raw_phone) = '')
                  AND (COALESCE(c.primary_email, sr.raw_email) IS NULL OR COALESCE(c.primary_email, sr.raw_email) = '')
                  AND (COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '')
                 THEN -2 ELSE 0 END
    )))
    FROM source_records sr
    WHERE sr.source_record_id = c.source_record_id
      AND c.is_ankara = TRUE
""")


def recalculate() -> int:
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(NEW_QUALITY_SQL, {"adres": "adres", "sektor": "sektor", "nace_code": "nace_code", "osb_parsel": "osb_parsel"})
        updated = result.rowcount or 0
        avg = conn.execute(text(
            "SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE"
        )).scalar()
    print(f"Guncellenen kayit sayisi: {updated}")
    print(f"Ortalama kalite skoru (Ankara+OSB): {avg}")
    return updated


def main() -> int:
    recalculate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
