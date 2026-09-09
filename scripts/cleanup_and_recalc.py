#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Bos kayitlari temizle ve kalite skorunu yeniden hesapla."""
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
        # Delete companies with NULL source_record_id and minimal data
        result = conn.execute(text("""
            DELETE FROM companies c
            WHERE c.source_record_id IS NULL
              AND (c.primary_phone IS NULL OR c.primary_phone = '')
              AND (c.primary_email IS NULL OR c.primary_email = '')
              AND (c.website_domain IS NULL OR c.website_domain = '')
              AND (c.adres IS NULL OR c.adres = '')
              AND (c.nace_code IS NULL OR c.nace_code = '')
              AND (c.vergi_no IS NULL OR c.vergi_no = '')
              AND (c.tax_number IS NULL OR c.tax_number = '')
        """))
        deleted = result.rowcount
        print(f"Silinen bos kayit: {deleted}")
    
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
        print(f"Kalan toplam: {total}")
    
    # Recalculate quality scores
    with engine.begin() as conn:
        result = conn.execute(text("""
            WITH base AS (
                SELECT c.company_id,
                       COALESCE(c.primary_phone, '') as phone,
                       COALESCE(c.primary_email, '') as email,
                       COALESCE(c.website_domain, '') as web,
                       COALESCE(c.adres, '') as adres,
                       COALESCE(c.nace_code, '') as nace,
                       COALESCE(c.vergi_no, c.tax_number, '') as vergi,
                       COALESCE(c.osb_parsel, '') as parsel,
                       COALESCE(sr.raw_payload, '{}'::jsonb) as payload
                FROM companies c
                LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
            ),
            scored AS (
                SELECT company_id,
                       (CASE WHEN phone != '' THEN 10 ELSE 0 END
                        + CASE WHEN email != '' THEN 5 ELSE 0 END
                        + CASE WHEN web != '' THEN 5 ELSE 0 END
                        + CASE WHEN adres != '' THEN 20 ELSE 0 END
                        + CASE WHEN nace != '' THEN 5 ELSE 0 END
                        + CASE WHEN vergi != '' THEN 20 ELSE 0 END
                        + CASE WHEN parsel != '' THEN 15 ELSE 0 END
                        + CASE WHEN payload->>'sektor' IS NOT NULL THEN 10 ELSE 0 END
                        + CASE WHEN payload->>'adres' IS NOT NULL AND adres = '' THEN 10 ELSE 0 END
                        - CASE WHEN vergi = '' AND payload->>'vergi_no' IS NULL THEN 15 ELSE 0 END
                        - CASE WHEN adres = '' AND payload->>'adres' IS NULL THEN 10 ELSE 0 END
                        - CASE WHEN web = '' AND payload->>'web_sitesi' IS NULL THEN 5 ELSE 0 END
                        - CASE WHEN phone = '' AND email = '' AND vergi = '' THEN 5 ELSE 0 END
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
    sys.exit(main())
