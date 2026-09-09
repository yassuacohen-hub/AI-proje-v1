import sys, re
sys.path.insert(0, "src")
from sqlalchemy import text
from company_master.db.connection import get_engine

f = open("scripts/recalculate_quality_scores.py", "r", encoding="utf-8")
s = f.read()
f.close()

m = re.search(r"NEW_QUALITY_SQL = text\(\"\"\"(.+?)\"\"\"\)", s, re.DOTALL)
sql = m.group(1)
print("penalties in sql:")
for line in sql.split("\n"):
    if "THEN -" in line:
        print(" ", line.strip())

# compute avg from SQL directly
engine = get_engine()
conn = engine.connect()
avg = conn.execute(text("""
    SELECT AVG(
        10
        + CASE WHEN COALESCE(c.primary_phone, sr.raw_phone) IS NOT NULL AND COALESCE(c.primary_phone, sr.raw_phone) <> '' THEN 10 ELSE 0 END
        + CASE WHEN COALESCE(c.primary_email, sr.raw_email) IS NOT NULL AND COALESCE(c.primary_email, sr.raw_email) <> '' THEN 5 ELSE 0 END
        + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NOT NULL AND COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) <> '' THEN 15 ELSE 0 END
        + CASE WHEN COALESCE(c.adres, sr.raw_payload->>'adres') IS NOT NULL AND COALESCE(c.adres, sr.raw_payload->>'adres') <> '' THEN 20 ELSE 0 END
        + CASE WHEN COALESCE(c.osb_parsel, sr.raw_payload->>'osb_parsel') IS NOT NULL AND COALESCE(c.osb_parsel, sr.raw_payload->>'osb_parsel') <> '' THEN 15 ELSE 0 END
        + CASE WHEN sr.raw_payload->>'sektor' IS NOT NULL AND sr.raw_payload->>'sektor' <> '' THEN 10 ELSE 0 END
        + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NOT NULL AND COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) <> '' THEN 20 ELSE 0 END
        + CASE WHEN (sr.raw_payload->>'nace_code' IS NOT NULL AND sr.raw_payload->>'nace_code' <> '') OR (sr.raw_nace IS NOT NULL AND sr.raw_nace <> '') THEN 5 ELSE 0 END
        + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '' THEN -8 ELSE 0 END
        + CASE WHEN COALESCE(c.adres, sr.raw_payload->>'adres') IS NULL OR COALESCE(c.adres, sr.raw_payload->>'adres') = '' THEN -5 ELSE 0 END
        + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NULL OR COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) = '' THEN -2 ELSE 0 END
        + CASE WHEN (COALESCE(c.primary_phone, sr.raw_phone) IS NULL OR COALESCE(c.primary_phone, sr.raw_phone) = '')
                  AND (COALESCE(c.primary_email, sr.raw_email) IS NULL OR COALESCE(c.primary_email, sr.raw_email) = '')
                  AND (COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '')
                 THEN -2 ELSE 0 END
    ) FROM companies c LEFT JOIN source_records sr ON sr.source_record_id=c.source_record_id WHERE c.is_ankara=TRUE
""")).scalar()
print("computed avg:", avg)

print("db avg:", conn.execute(text("SELECT AVG(data_quality_score) FROM companies WHERE is_ankara=TRUE")).scalar())
conn.close()
