-- Migration 0011 down: Dashboard search optimization
-- Migration 0011_dashboard_search_optimization.sql'in tersidir

DROP INDEX IF EXISTS idx_companies_search_text_trgm;
DROP INDEX IF EXISTS idx_companies_source_record_score;
DROP INDEX IF EXISTS idx_source_records_covering;

ALTER TABLE companies DROP COLUMN IF EXISTS search_text;