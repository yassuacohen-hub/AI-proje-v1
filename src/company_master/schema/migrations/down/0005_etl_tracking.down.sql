-- Migration 0005 down: source_records → companies izleme sütununu geri al
-- Migration 0005_etl_tracking.sql'in tersidir

ALTER TABLE companies DROP COLUMN IF EXISTS source_record_id;
DROP INDEX IF EXISTS idx_companies_source_record;