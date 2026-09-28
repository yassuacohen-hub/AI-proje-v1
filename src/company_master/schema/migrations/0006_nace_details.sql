-- Migration 0006: NACE kodu ve kaynağı detay sütunları
-- Amaç: Eksik NACE için varsayılan değer atama ve geçerlilik takibi.
-- normalize.py artık nace_code, nace_name ve nace_source sütunlarını doldurur.

ALTER TABLE companies ADD COLUMN IF NOT EXISTS nace_code TEXT;
-- dusen-iz: companies.nace_name
-- D-268: bu kolon goc 0036 ile dusuruldu (olculdu: 8289 satirin 52sinde deger
-- vardi, degerler NACE adi degil serbest sektor metniydi, uretimde tuketicisi
-- yoktu). Satir tarihsel kayit olarak duruyor; izi ARANMAZ.
ALTER TABLE companies ADD COLUMN IF NOT EXISTS nace_name TEXT;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS nace_source TEXT DEFAULT 'unknown' CHECK (nace_source IN ('mersis', 'external', 'predicted', 'sector_default', 'title_default', 'fallback', 'unknown'));
CREATE INDEX IF NOT EXISTS idx_companies_nace_code ON companies(nace_code);
