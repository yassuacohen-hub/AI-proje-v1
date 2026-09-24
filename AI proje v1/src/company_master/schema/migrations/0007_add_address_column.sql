-- Migration 0007: Add address column and supporting indexes
ALTER TABLE companies ADD COLUMN IF NOT EXISTS adres TEXT;
CREATE INDEX IF NOT EXISTS idx_companies_adres ON companies(adres);
