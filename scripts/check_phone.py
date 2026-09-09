import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()

with engine.connect() as conn:
    # Debug: check formula components for a few records
    print("=== Formül bileşenleri - örnek 5 kayıt ===\n")

    result = conn.execute(text("""
        SELECT
            c.company_id,
            c.primary_phone,
            sr.raw_phone,
            c.primary_email,
            sr.raw_email,
            COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) as website,
            sr.raw_payload->>'adres' as adres,
            sr.raw_payload->>'sektor' as sektor,
            COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) as tax,
            c.osb_parsel,
            (sr.raw_payload->>'nace_code') IS NOT NULL as nace_present,
            c.data_quality_score
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara = TRUE
        LIMIT 5
    """)).fetchall()

    for i, r in enumerate(result):
        print(f"Kayıt {i+1} ({r[0]}):")
        print(f"  primary_phone={r[1]}, raw_phone={r[2]}")
        print(f"  primary_email={r[3]}, raw_email={r[4]}")
        print(f"  website={r[5]}")
        print(f"  adres={r[6]}")
        print(f"  sektor={r[7]}")
        print(f"  tax={r[8]}")
        print(f"  osb_parsel={r[9]}")
        print(f"  nace_present={r[10]}")
        print(f"  SCORE={r[11]}")
        print()

    # Now trace the formula for a record with score 0
    print("=== Score=0 kayıt formül izleme ===")
    result = conn.execute(text("""
        SELECT
            c.company_id,
            -- Component scores
            CASE WHEN COALESCE(c.primary_phone, sr.raw_phone) IS NOT NULL AND COALESCE(c.primary_phone, sr.raw_phone) <> '' THEN 10 ELSE 0 END as phone_score,
            CASE WHEN COALESCE(c.primary_email, sr.raw_email) IS NOT NULL AND COALESCE(c.primary_email, sr.raw_email) <> '' THEN 5 ELSE 0 END as email_score,
            CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NOT NULL AND COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) <> '' THEN 15 ELSE 0 END as web_score,
            CASE WHEN sr.raw_payload->>'adres' IS NOT NULL AND sr.raw_payload->>'adres' <> '' THEN 20 ELSE 0 END as adres_score,
            CASE WHEN sr.raw_payload->>'sektor' IS NOT NULL AND sr.raw_payload->>'sektor' <> '' THEN 10 ELSE 0 END as sektor_score,
            CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NOT NULL AND COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) <> '' THEN 20 ELSE 0 END as tax_score,
            CASE WHEN c.osb_parsel IS NOT NULL AND c.osb_parsel <> '' THEN 15 ELSE 0 END as parsel_score,
            CASE WHEN (sr.raw_payload->>'nace_code' IS NOT NULL AND sr.raw_payload->>'nace_code' <> '') OR sr.raw_nace IS NOT NULL THEN 5 ELSE 0 END as nace_score,
            -- Penalties
            CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '' THEN 15 ELSE 0 END as tax_penalty,
            CASE WHEN sr.raw_payload->>'adres' IS NULL OR sr.raw_payload->>'adres' = '' THEN 10 ELSE 0 END as adres_penalty,
            CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NULL OR COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) = '' THEN 5 ELSE 0 END as web_penalty,
            CASE WHEN (COALESCE(c.primary_phone, sr.raw_phone) IS NULL OR COALESCE(c.primary_phone, sr.raw_phone) = '') AND (COALESCE(c.primary_email, sr.raw_email) IS NULL OR COALESCE(c.primary_email, sr.raw_email) = '') AND (COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '') THEN 5 ELSE 0 END as all_empty_penalty,
            c.data_quality_score
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara = TRUE AND c.data_quality_score = 0
        LIMIT 3
    """)).fetchall()

    for i, r in enumerate(result):
        print(f"Kayıt {i+1} ({r[0]}):")
        print(f"  phone={r[1]}, email={r[2]}, web={r[3]}, adres={r[4]}, sektor={r[5]}, tax={r[6]}, parsel={r[7]}, nace={r[8]}")
        print(f"  penalties: tax={r[9]}, adres={r[10]}, web={r[11]}, all_empty={r[12]}")
        total = r[1]+r[2]+r[3]+r[4]+r[5]+r[6]+r[7]+r[8]-r[9]-r[10]-r[11]-r[12]
        print(f"  Toplam hesaplanan: {total}, db_score={r[13]}")
        print()