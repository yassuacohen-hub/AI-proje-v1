-- Migration 0009 down: Dashboard slow query indexes
-- Migration 0009_dashboard_performance.sql'in tersidir

DROP INDEX IF EXISTS idx_companies_ankara_osb_score;
DROP INDEX IF EXISTS idx_companies_vergi_no;
DROP INDEX IF EXISTS idx_companies_primary_phone;
DROP INDEX IF EXISTS idx_companies_primary_email;
DROP INDEX IF EXISTS idx_companies_web_sitesi;
DROP INDEX IF EXISTS idx_companies_legal_name_lower;
DROP INDEX IF EXISTS idx_companies_trade_name_lower;
DROP INDEX IF EXISTS idx_companies_created_at;