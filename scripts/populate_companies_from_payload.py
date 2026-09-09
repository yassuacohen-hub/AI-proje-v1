import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()

with engine.begin() as conn:
    # Update companies directly from raw_payload using JSONB extraction
    sql = text("""
        UPDATE companies c
        SET 
            primary_phone = COALESCE(c.primary_phone, NULLIF(sr.raw_payload->>'telefoner', '')),
            web_sitesi = COALESCE(c.web_sitesi, NULLIF(sr.raw_payload->>'web_sitesi', '')),
            vergi_no = COALESCE(c.vergi_no, NULLIF(sr.raw_payload->>'vergi_no', '')),
            nace_validity = COALESCE(c.nace_validity, NULLIF(sr.raw_payload->>'nace_code', '')),
            osb_parsel = COALESCE(c.osb_parsel, NULLIF(sr.raw_payload->>'osb_parsel', '')),
            website_domain = COALESCE(c.website_domain, NULLIF(sr.raw_payload->>'web_sitesi', ''))
        FROM source_records sr
        WHERE c.source_record_id = sr.source_record_id
          AND c.is_ankara = TRUE
          AND sr.raw_payload IS NOT NULL
    """)
    result = conn.execute(sql)
    print(f"Step 1 - Updated companies from raw_payload: {result.rowcount} rows")
    
    # Count results
    avg = conn.execute(text("SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE")).scalar()
    print(f"Current avg quality score: {avg}")