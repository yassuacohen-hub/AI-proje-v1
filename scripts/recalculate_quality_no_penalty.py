#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DB kalite skorlarini yeniden hesapla - daha yuksek puanlar."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
BATCH_SIZE = 500

with engine.connect() as conn:
    total = conn.execute(text("""
        SELECT COUNT(*) FROM companies 
        WHERE is_ankara = TRUE AND is_osb_member = TRUE
    """)).scalar()
    
    print(f"Toplam firma: {total}")
    
    offset = 0
    updated = 0
    
    while offset < total:
        scores = conn.execute(text("""
            WITH batch AS (
                SELECT c.company_id,
                    (
                        10
                        + CASE WHEN COALESCE(c.primary_phone, sr.raw_phone) IS NOT NULL
                                    AND COALESCE(c.primary_phone, sr.raw_phone) <> '' THEN 10 ELSE 0 END
                        + CASE WHEN COALESCE(c.primary_email, sr.raw_email) IS NOT NULL
                                    AND COALESCE(c.primary_email, sr.raw_email) <> '' THEN 5 ELSE 0 END
                        + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NOT NULL
                                    AND COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) <> '' THEN 15 ELSE 0 END
                        + CASE WHEN sr.raw_payload->>'adres' IS NOT NULL
                                    AND sr.raw_payload->>'adres' <> '' THEN 20 ELSE 0 END
                        + CASE WHEN sr.raw_payload->>'sektor' IS NOT NULL
                                    AND sr.raw_payload->>'sektor' <> '' THEN 10 ELSE 0 END
                        + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NOT NULL
                                    AND COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) <> '' THEN 20 ELSE 0 END
                        + CASE WHEN c.osb_parsel IS NOT NULL AND c.osb_parsel <> '' THEN 15 ELSE 0 END
                        + CASE WHEN (sr.raw_payload->>'nace_code' IS NOT NULL
                                      AND sr.raw_payload->>'nace_code' <> '')
                                    OR (sr.raw_nace IS NOT NULL AND sr.raw_nace <> '') THEN 5 ELSE 0 END
                    ) AS new_score
                FROM companies c
                LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
                WHERE c.is_ankara = TRUE AND c.is_osb_member = TRUE
                ORDER BY c.company_id
                LIMIT :limit OFFSET :offset
            )
            UPDATE companies c
            SET data_quality_score = GREATEST(0, LEAST(100, batch.new_score))
            FROM batch
            WHERE c.company_id = batch.company_id
        """), {"limit": BATCH_SIZE, "offset": offset})
        
        batch_updated = scores.rowcount or 0
        updated += batch_updated
        print(f"Batch {offset//BATCH_SIZE + 1}: {batch_updated} kayit")
        
        offset += BATCH_SIZE
        conn.commit()
    
    avg = conn.execute(text("""
        SELECT AVG(data_quality_score) FROM companies 
        WHERE is_ankara = TRUE AND is_osb_member = TRUE
    """)).scalar()
    
    print(f"Toplam: {updated}, Ortalama: {avg:.2f}")
