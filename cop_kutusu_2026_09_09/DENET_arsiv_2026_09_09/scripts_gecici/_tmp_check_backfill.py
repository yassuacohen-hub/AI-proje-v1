import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text
engine = get_engine()
conn = engine.connect()

queries = [
    ("sektor from raw_payload", "SELECT COUNT(*) FROM source_records WHERE raw_payload ? 'sektor' AND NULLIF(raw_payload->>'sektor', '') IS NOT NULL"),
    ("nace_code from raw_payload", "SELECT COUNT(*) FROM source_records WHERE raw_payload ? 'nace_code' AND NULLIF(raw_payload->>'nace_code', '') IS NOT NULL"),
    ("companies with raw_phone missing primary_phone", "SELECT COUNT(*) FROM companies c JOIN source_records sr ON c.source_record_id = sr.source_record_id WHERE (c.primary_phone IS NULL OR c.primary_phone = '') AND sr.raw_phone IS NOT NULL AND NULLIF(sr.raw_phone, '') IS NOT NULL"),
    ("companies with raw_email missing primary_email", "SELECT COUNT(*) FROM companies c JOIN source_records sr ON c.source_record_id = sr.source_record_id WHERE (c.primary_email IS NULL OR c.primary_email = '') AND sr.raw_email IS NOT NULL AND NULLIF(sr.raw_email, '') IS NOT NULL"),
    ("companies with raw_website missing website_domain", "SELECT COUNT(*) FROM companies c JOIN source_records sr ON c.source_record_id = sr.source_record_id WHERE (c.website_domain IS NULL OR c.website_domain = '') AND sr.raw_website IS NOT NULL AND NULLIF(sr.raw_website, '') IS NOT NULL"),
]
for label, sql in queries:
    r = conn.execute(text(sql)).scalar()
    print(f"{label}: {r}")
