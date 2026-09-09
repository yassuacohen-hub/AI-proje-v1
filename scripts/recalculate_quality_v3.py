#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DB kalite skorlarini yeniden hesapla - daha dengeli formul."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

NEW_QUALITY_SQL = text("""
    WITH scored AS (
        SELECT
            c.company_id,
            (
                5
                + CASE WHEN COALESCE(c.primary_phone, sr.raw_phone) IS NOT NULL
                            AND COALESCE(c.primary_phone, sr.raw_phone) <> '' THEN 10 ELSE 0 END
                + CASE WHEN COALESCE(c.primary_email, sr.raw_email) IS NOT NULL
                            AND COALESCE(c.primary_email, sr.raw_email) <> '' THEN 5 ELSE 0 END
                + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NOT NULL
                            AND COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) <> '' THEN 15 ELSE 0 END
                + CASE WHEN sr.raw_payload->>:adres IS NOT NULL
                            AND sr.raw_payload->>:adres <> '' THEN 20 ELSE 0 END
                + CASE WHEN sr.raw_payload->>:sektor IS NOT NULL
                            AND sr.raw_payload->>:sektor <> '' THEN 10 ELSE 0 END
                + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NOT NULL
                            AND COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) <> '' THEN 20 ELSE 0 END
                + CASE WHEN c.osb_parsel IS NOT NULL AND c.osb_parsel <> '' THEN 15 ELSE 0 END
                + CASE WHEN (sr.raw_payload->>:nace_code IS NOT NULL
                              AND sr.raw_payload->>:nace_code <> '')
                            OR (sr.raw_nace IS NOT NULL AND sr.raw_nace <> '') THEN 5 ELSE 0 END
                + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL
                            OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '' THEN -3 ELSE 0 END
                + CASE WHEN NOT sr.raw_payload ? :adres THEN -3 ELSE 0 END
                + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NULL
                            OR COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) = '' THEN -3 ELSE 0 END
            ) AS new_score
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
    )
    UPDATE companies c
    SET data_quality_score = GREATEST(0, LEAST(100, scored.new_score))
    FROM scored
    WHERE c.company_id = scored.company_id
""")

def recalculate() -> int:
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(NEW_QUALITY_SQL, {"adres": "adres", "sektor": "sektor", "nace_code": "nace_code"})
        updated = result.rowcount or 0
        avg = conn.execute(text(
            "SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE AND is_osb_member = TRUE"
        )).scalar()
    print(f"Guncellenen kayit sayisi: {updated}")
    print(f"Ortalama kalite skoru (Ankara+OSB): {avg:.2f}")
    return updated

if __name__ == "__main__":
    recalculate()
