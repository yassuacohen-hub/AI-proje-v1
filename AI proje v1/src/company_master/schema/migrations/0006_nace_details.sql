-- Migration 0006: NACE kodu ve kaynağı detay sütunları
-- Amaç: Eksik NACE için varsayılan değer atama ve geçerlilik takibi.
-- normalize.py artık nace_code, nace_name ve nace_source sütunlarını doldurur.

ALTER TABLE companies ADD COLUMN IF NOT EXISTS nace_code TEXT;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS nace_name TEXT;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS nace_source TEXT DEFAULT 'unknown' CHECK (nace_source IN ('mersis', 'external', 'predicted', 'sector_default', 'title_default', 'fallback', 'unknown'));
CREATE INDEX IF NOT EXISTS idx_companies_nace_code ON companies(nace_code);
