-- Migration 0008: Performance indexes for dashboard queries
CREATE INDEX IF NOT EXISTS idx_companies_ankara_osb ON companies(is_ankara, is_osb_member);
CREATE INDEX IF NOT EXISTS idx_companies_quality_score ON companies(data_quality_score);
CREATE INDEX IF NOT EXISTS idx_companies_source_record ON companies(source_record_id);
CREATE INDEX IF NOT EXISTS idx_companies_legal_name_trgm ON companies USING gin(legal_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_companies_trade_name_trgm ON companies USING gin(trade_name gin_trgm_ops);
