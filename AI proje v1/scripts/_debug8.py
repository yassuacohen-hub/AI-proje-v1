import sys
sys.path.insert(0, "src")
from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
conn = engine.connect()

# Run script SQL with literal strings instead of parameters
literal_sql = """
    WITH scored AS (
        SELECT
            c.company_id,
            (
                CASE WHEN COALESCE(c.primary_phone, sr.raw_phone) IS NOT NULL
                          AND COALESCE(c.primary_phone, sr.raw_phone) <> '' THEN 10 ELSE 0 END
                + CASE WHEN COALESCE(c.primary_email, sr.raw_email) IS NOT NULL
                            AND COALESCE(c.primary_email, sr.raw_email) <> '' THEN 5 ELSE 0 END
                + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NOT NULL
                            AND COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) <> '' THEN 15 ELSE 0 END
                + CASE WHEN COALESCE(c.adres, sr.raw_payload->>'adres') IS NOT NULL
                            AND COALESCE(c.adres, sr.raw_payload->>'adres') <> '' THEN 20 ELSE 0 END
                + CASE WHEN COALESCE(c.osb_parsel, sr.raw_payload->>'osb_parsel') IS NOT NULL
                            AND COALESCE(c.osb_parsel, sr.raw_payload->>'osb_parsel') <> '' THEN 15 ELSE 0 END
                + CASE WHEN sr.raw_payload->>'sektor' IS NOT NULL
                            AND sr.raw_payload->>'sektor' <> '' THEN 10 ELSE 0 END
                + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NOT NULL
                            AND COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) <> '' THEN 20 ELSE 0 END
                + CASE WHEN (sr.raw_payload->>'nace_code' IS NOT NULL
                              AND sr.raw_payload->>'nace_code' <> '')
                            OR (sr.raw_nace IS NOT NULL AND sr.raw_nace <> '') THEN 5 ELSE 0 END
                + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL
                            OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '' THEN -8 ELSE 0 END
                + CASE WHEN COALESCE(c.adres, sr.raw_payload->>'adres') IS NULL
                            OR COALESCE(c.adres, sr.raw_payload->>'adres') = '' THEN -5 ELSE 0 END
                + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NULL
                            OR COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) = '' THEN -2 ELSE 0 END
                + CASE WHEN (COALESCE(c.primary_phone, sr.raw_phone) IS NULL OR COALESCE(c.primary_phone, sr.raw_phone) = '')
                          AND (COALESCE(c.primary_email, sr.raw_email) IS NULL OR COALESCE(c.primary_email, sr.raw_email) = '')
                          AND (COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '')
                         THEN -2 ELSE 0 END
            ) AS new_score
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
    )
    UPDATE companies c
    SET data_quality_score = GREATEST(0, LEAST(100, scored.new_score))
    FROM scored
    WHERE c.company_id = scored.company_id
"""

result = conn.execute(text(literal_sql))
print("updated:", result.rowcount)
avg = conn.execute(text("SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE")).scalar()
print("avg after literal exec:", avg)
conn.close()
