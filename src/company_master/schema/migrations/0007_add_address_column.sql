-- Migration 0007: Add address column and supporting indexes
--
-- ustunden-gecen: 0027_ikiz_kolonlari_birlestir.sql
-- Bu gocun tum izi (adres kolonu + indeksi) 0027'de address/
-- idx_companies_address olarak yeniden adlandirildi (D-251/1).
ALTER TABLE companies ADD COLUMN IF NOT EXISTS adres TEXT;
CREATE INDEX IF NOT EXISTS idx_companies_adres ON companies(adres);
