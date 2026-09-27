-- Migration down: source_records.company_id kolonu kaldır

DROP INDEX IF EXISTS idx_source_records_company_id;
ALTER TABLE source_records DROP COLUMN IF EXISTS company_id;