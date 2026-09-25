-- Migration 0007 down: Add address column and supporting indexes
-- Migration 0007_add_address_column.sql'in tersidir

DROP INDEX IF EXISTS idx_companies_adres;
ALTER TABLE companies DROP COLUMN IF EXISTS adres;