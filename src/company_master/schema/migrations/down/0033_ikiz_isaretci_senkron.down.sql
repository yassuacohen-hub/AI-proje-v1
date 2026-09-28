-- 0033 geri alma.
-- NOT: doldurulan 5052 company_id degeri GERI ALINMAZ.
--   Bunlar dogru veri; geri almak veri kaybi olur (D-262).
--   Sadece trigger ve COMMENT kaldirilir.

BEGIN;

DROP TRIGGER IF EXISTS companies_isaretci_senkron ON companies;
DROP FUNCTION IF EXISTS trg_isaretci_senkron();

COMMENT ON COLUMN companies.source_record_id IS NULL;
COMMENT ON COLUMN source_records.company_id IS NULL;

COMMIT;
