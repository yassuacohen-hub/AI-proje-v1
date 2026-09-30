-- Migration 0043 down: companies.sector_name, sector_source kolonlarını kaldır

DROP INDEX IF EXISTS idx_companies_sector_name;
DROP INDEX IF EXISTS idx_companies_sector_source;
ALTER TABLE companies DROP COLUMN IF EXISTS sector_name;
ALTER TABLE companies DROP COLUMN IF EXISTS sector_source;