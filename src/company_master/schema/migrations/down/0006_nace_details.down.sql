-- Migration 0006 down: NACE detay sütunlarını geri al
-- Migration 0006_nace_details.sql'in tersidir

DROP INDEX IF EXISTS idx_companies_nace_code;
ALTER TABLE companies DROP COLUMN IF EXISTS nace_code;
ALTER TABLE companies DROP COLUMN IF EXISTS nace_name;
ALTER TABLE companies DROP COLUMN IF EXISTS nace_source;