-- Migration 0022 down: companies.legal_name UNIQUE kısıtını kaldır

DROP INDEX IF EXISTS uq_companies_legal_name;

-- Eğer CONSTRAINT eklendiyse:
-- ALTER TABLE companies DROP CONSTRAINT IF EXISTS uq_companies_legal_name;