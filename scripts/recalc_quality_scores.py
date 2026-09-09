#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tum firmalar icin kalite skorunu yeniden hesapla (SQL, deadlock-free)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine
from sqlalchemy import text


def main() -> int:
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(text("""
            WITH base AS (
                SELECT c.company_id,
                       c.source_record_id,
                       c.data_freshness_score,
                       c.phone_format_score,
                       c.social_media_score,
                       c.source_diversity_score,
                       c.job_postings_score,
                       c.employee_count_score,
                       c.email_validity_score,
                       COALESCE(c.primary_phone, '') as phone,
                       COALESCE(c.primary_email, '') as email,
                       COALESCE(c.website_domain, '') as web,
                       COALESCE(c.adres, '') as adres,
                       COALESCE(c.nace_code, '') as nace,
                       COALESCE(c.vergi_no, c.tax_number, '') as vergi,
                       COALESCE(c.osb_parsel, '') as parsel,
                       CASE WHEN c.source_record_id IS NOT NULL THEN COALESCE(sr.raw_payload, '{}'::jsonb) ELSE '{}'::jsonb END as payload,
                       sr.raw_phone, sr.raw_email, sr.raw_website, sr.raw_tax_number
                FROM companies c
                LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
            ),
            scored AS (
                SELECT company_id,
                       (CASE WHEN COALESCE(phone, raw_phone, '') != '' THEN 15 ELSE 0 END
                        + CASE WHEN COALESCE(email, raw_email, '') != '' THEN 10 ELSE 0 END
                        + CASE WHEN COALESCE(web, raw_website, '') != '' THEN 10 ELSE 0 END
                        + CASE WHEN adres != '' OR payload->>'adres' IS NOT NULL THEN 10 ELSE 0 END
                        + CASE WHEN nace != '' THEN 15 ELSE 0 END
                        + CASE WHEN vergi != '' OR raw_tax_number IS NOT NULL THEN 10 ELSE 0 END
                        + CASE WHEN parsel != '' THEN 5 ELSE 0 END
                        + CASE WHEN payload->>'sektor' IS NOT NULL THEN 10 ELSE 0 END
                        + CASE WHEN source_record_id IS NOT NULL THEN 5 ELSE 0 END
                        + CASE WHEN (SELECT count(*) FROM jsonb_object_keys(payload)) > 0 THEN 5 ELSE 0 END
                        + COALESCE(data_freshness_score, 0)
                        + COALESCE(phone_format_score, 0)
                        + COALESCE(social_media_score, 0)
                        + COALESCE(source_diversity_score, 0)
                        + COALESCE(job_postings_score, 0)
                        + COALESCE(employee_count_score, 0)
                        + COALESCE(email_validity_score, 0)
                        - CASE WHEN vergi = '' AND raw_tax_number IS NULL AND payload->>'vergi_no' IS NULL THEN 5 ELSE 0 END
                        - CASE WHEN adres = '' AND payload->>'adres' IS NULL THEN 3 ELSE 0 END
                        - CASE WHEN COALESCE(web, raw_website, '') = '' AND payload->>'web_sitesi' IS NULL THEN 2 ELSE 0 END
                        - CASE WHEN COALESCE(phone, raw_phone, '') = '' AND COALESCE(email, raw_email, '') = '' AND vergi = '' AND raw_tax_number IS NULL THEN 2 ELSE 0 END
                       ) as raw_score
                FROM base
            )
            UPDATE companies c
            SET data_quality_score = LEAST(GREATEST(s.raw_score, 0), 100),
                updated_at = NOW()
            FROM scored s
            WHERE c.company_id = s.company_id
        """))
        updated = result.rowcount
    
    print(f"Guncellenen: {updated} firma")
    
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT CASE WHEN data_quality_score >= 80 THEN '80-100' WHEN data_quality_score >= 60 THEN '60-79' WHEN data_quality_score >= 40 THEN '40-59' WHEN data_quality_score >= 20 THEN '20-39' ELSE '0-19' END as bucket, COUNT(*) as cnt FROM companies GROUP BY 1 ORDER BY 1 DESC")).mappings().all()
        print('\nYeni kalite dagilimi:')
        for r in rows:
            print(f"  {r['bucket']}: {r['cnt']}")
        
        avg = conn.execute(text("SELECT AVG(data_quality_score) FROM companies")).scalar()
        print(f'\nYeni ortalama skor: {avg:.2f}')
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
