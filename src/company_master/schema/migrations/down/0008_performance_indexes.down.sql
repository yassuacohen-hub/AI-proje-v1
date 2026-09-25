-- Migration 0008 down: Performance indexes
-- Migration 0008_performance_indexes.sql'in tersidir

DROP INDEX IF EXISTS idx_companies_ankara_osb;
DROP INDEX IF EXISTS idx_companies_quality_score;
DROP INDEX IF NOT EXISTS idx_companies_source_record;
DROP INDEX IF NOT EXISTS idx_companies_legal_name_trgm;
DROP INDEX IF NOT EXISTS idx_companies_trade_name_trgm;