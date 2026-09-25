-- Migration 0010 down: Additional performance indexes for dashboard optimization
-- Migration 0010_dashboard_optimization.sql'in tersidir

DROP INDEX IF EXISTS idx_companies_tax_number_lower;
DROP INDEX IF EXISTS idx_companies_vergi_no_lower;
DROP INDEX IF EXISTS idx_sources_source_name;
DROP INDEX IF EXISTS idx_companies_kpi_covering;