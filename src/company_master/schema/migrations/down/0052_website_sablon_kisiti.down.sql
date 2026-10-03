-- 0052 geri alma.
-- NOT: NULL'a cekilen 2666 website_domain GERI YAZILMAZ; ham deger
--   source_records.raw_payload icinde ve yedekler/companies_website_sablon_*.jsonl
--   dosyasinda durur. Sadece trigger ve COMMENT kaldirilir.

BEGIN;

DROP TRIGGER IF EXISTS companies_website_sablon ON companies;
DROP FUNCTION IF EXISTS trg_website_sablon_temizle();
COMMENT ON COLUMN companies.website_domain IS NULL;

COMMIT;
