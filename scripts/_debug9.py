import sys
sys.path.insert(0, "src")
from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
conn = engine.connect()

# compute raw scores without clamping
rows = conn.execute(text("""
    SELECT 
        COUNT(*) FILTER (WHERE raw_score < 0) as neg,
        COUNT(*) FILTER (WHERE raw_score > 100) as over,
        COUNT(*) FILTER (WHERE raw_score = 0) as zero,
        AVG(raw_score) as avg_raw,
        AVG(GREATEST(0, LEAST(100, raw_score))) as avg_clamped
    FROM (
        SELECT 
            (10
             + CASE WHEN COALESCE(primary_phone, sr.raw_phone) IS NOT NULL AND COALESCE(primary_phone, sr.raw_phone) <> '' THEN 10 ELSE 0 END
             + CASE WHEN COALESCE(primary_email, sr.raw_email) IS NOT NULL AND COALESCE(primary_email, sr.raw_email) <> '' THEN 5 ELSE 0 END
             + CASE WHEN COALESCE(website_domain, sr.raw_website, web_sitesi) IS NOT NULL AND COALESCE(website_domain, sr.raw_website, web_sitesi) <> '' THEN 15 ELSE 0 END
             + CASE WHEN COALESCE(adres, sr.raw_payload->>'adres') IS NOT NULL AND COALESCE(adres, sr.raw_payload->>'adres') <> '' THEN 20 ELSE 0 END
             + CASE WHEN COALESCE(osb_parsel, sr.raw_payload->>'osb_parsel') IS NOT NULL AND COALESCE(osb_parsel, sr.raw_payload->>'osb_parsel') <> '' THEN 15 ELSE 0 END
             + CASE WHEN sr.raw_payload->>'sektor' IS NOT NULL AND sr.raw_payload->>'sektor' <> '' THEN 10 ELSE 0 END
             + CASE WHEN COALESCE(tax_number, vergi_no, sr.raw_tax_number) IS NOT NULL AND COALESCE(tax_number, vergi_no, sr.raw_tax_number) <> '' THEN 20 ELSE 0 END
             + CASE WHEN (sr.raw_payload->>'nace_code' IS NOT NULL AND sr.raw_payload->>'nace_code' <> '') OR (sr.raw_nace IS NOT NULL AND sr.raw_nace <> '') THEN 5 ELSE 0 END
             + CASE WHEN COALESCE(tax_number, vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(tax_number, vergi_no, sr.raw_tax_number) = '' THEN -8 ELSE 0 END
             + CASE WHEN COALESCE(adres, sr.raw_payload->>'adres') IS NULL OR COALESCE(adres, sr.raw_payload->>'adres') = '' THEN -5 ELSE 0 END
             + CASE WHEN COALESCE(website_domain, sr.raw_website, web_sitesi) IS NULL OR COALESCE(website_domain, sr.raw_website, web_sitesi) = '' THEN -2 ELSE 0 END
             + CASE WHEN (COALESCE(primary_phone, sr.raw_phone) IS NULL OR COALESCE(primary_phone, sr.raw_phone) = '')
                       AND (COALESCE(primary_email, sr.raw_email) IS NULL OR COALESCE(primary_email, sr.raw_email) = '')
                       AND (COALESCE(tax_number, vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(tax_number, vergi_no, sr.raw_tax_number) = '')
                      THEN -2 ELSE 0 END
        ) as raw_score
    FROM companies c LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
    WHERE c.is_ankara = TRUE
) s
""")).fetchone()
print("negative:", rows[0])
print("over 100:", rows[1])
print("zero:", rows[2])
print("avg raw:", rows[3])
print("avg clamped:", rows[4])
conn.close()
