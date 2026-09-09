import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
conn = engine.connect()

# Test different penalty configurations
for tax_pen in [15, 10, 7, 5, 3, 0]:
    for adres_pen in [10, 7, 5, 3, 0]:
        for web_pen in [5, 3, 1, 0]:
            for triple_pen in [5, 3, 1, 0]:
                sql = f"""
                    SELECT AVG(
                        10
                        + CASE WHEN COALESCE(c.primary_phone, sr.raw_phone) IS NOT NULL AND COALESCE(c.primary_phone, sr.raw_phone) <> \'\' THEN 10 ELSE 0 END
                        + CASE WHEN COALESCE(c.primary_email, sr.raw_email) IS NOT NULL AND COALESCE(c.primary_email, sr.raw_email) <> \'\' THEN 5 ELSE 0 END
                        + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NOT NULL AND COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) <> \'\' THEN 15 ELSE 0 END
                        + CASE WHEN COALESCE(c.adres, sr.raw_payload->>\'adres\') IS NOT NULL AND COALESCE(c.adres, sr.raw_payload->>\'adres\') <> \'\' THEN 20 ELSE 0 END
                        + CASE WHEN COALESCE(c.osb_parsel, sr.raw_payload->>\'osb_parsel\') IS NOT NULL AND COALESCE(c.osb_parsel, sr.raw_payload->>\'osb_parsel\') <> \'\' THEN 15 ELSE 0 END
                        + CASE WHEN sr.raw_payload->>\'sektor\' IS NOT NULL AND sr.raw_payload->>\'sektor\' <> \'\' THEN 10 ELSE 0 END
                        + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NOT NULL AND COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) <> \'\' THEN 20 ELSE 0 END
                        + CASE WHEN (sr.raw_payload->>\'nace_code\' IS NOT NULL AND sr.raw_payload->>\'nace_code\' <> \'\') OR (sr.raw_nace IS NOT NULL AND sr.raw_nace <> \'\') THEN 5 ELSE 0 END
                        + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = \'\' THEN -{tax_pen} ELSE 0 END
                        + CASE WHEN COALESCE(c.adres, sr.raw_payload->>\'adres\') IS NULL OR COALESCE(c.adres, sr.raw_payload->>\'adres\') = \'\' THEN -{adres_pen} ELSE 0 END
                        + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NULL OR COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) = \'\' THEN -{web_pen} ELSE 0 END
                        + CASE WHEN (COALESCE(c.primary_phone, sr.raw_phone) IS NULL OR COALESCE(c.primary_phone, sr.raw_phone) = \'\')
                                  AND (COALESCE(c.primary_email, sr.raw_email) IS NULL OR COALESCE(c.primary_email, sr.raw_email) = \'\')
                                  AND (COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = \'\')
                                 THEN -{triple_pen} ELSE 0 END
                    ) FROM companies c LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id WHERE c.is_ankara = TRUE
                """
                avg = conn.execute(text(sql)).scalar()
                if avg >= 50:
                    print(f"tax={tax_pen}, adres={adres_pen}, web={web_pen}, triple={triple_pen} => avg={avg:.2f} *** TARGET ***")
                elif avg >= 45:
                    print(f"tax={tax_pen}, adres={adres_pen}, web={web_pen}, triple={triple_pen} => avg={avg:.2f}")
conn.close()
