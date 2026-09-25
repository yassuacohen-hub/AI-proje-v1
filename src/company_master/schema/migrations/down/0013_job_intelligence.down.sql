-- Migration 0013 down: Job Intelligence Module tables
-- Migration 0013_job_intelligence.sql'in tersidir

-- Views (views don't have dependencies on other objects created in this migration)
DROP VIEW IF EXISTS v_company_active_signals;
DROP VIEW IF EXISTS v_company_job_summary;

-- Triggers
DROP TRIGGER IF EXISTS update_company_tech_profile_updated_at ON company_tech_profile;
DROP TRIGGER IF EXISTS update_company_intel_scores_updated_at ON company_intelligence_scores;
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Tables (FK dependency order)
DROP TABLE IF EXISTS company_aliases;
DROP TABLE IF EXISTS company_tech_profile;
DROP TABLE IF EXISTS company_intelligence_scores;
DROP TABLE IF EXISTS company_signals;
DROP TABLE IF EXISTS job_postings;