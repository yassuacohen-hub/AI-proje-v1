-- Migration 0014 down: Paket ve Pazarlama tablolarını geri al
-- Migration 0014_packages_marketing.sql'in tersidir

DROP TABLE IF EXISTS segment_companies;
DROP TABLE IF EXISTS campaign_segments;
DROP INDEX IF EXISTS idx_segments_active;
DROP INDEX IF EXISTS idx_segments_name;
DROP TABLE IF EXISTS segments;
DROP INDEX IF NOT EXISTS idx_campaigns_status;
DROP INDEX IF NOT EXISTS idx_campaigns_name;
DROP TABLE IF EXISTS campaigns;
DROP INDEX IF NOT EXISTS idx_cp_company;
DROP INDEX IF NOT EXISTS idx_cp_package;
DROP TABLE IF EXISTS company_packages;
DROP INDEX IF NOT EXISTS idx_packages_name;
DROP INDEX IF NOT EXISTS idx_packages_active;
DROP TABLE IF EXISTS packages;