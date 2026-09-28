-- Migration 0025 down: kimlik dosyasi alanlari + puan surumu kaldirilir.
--
-- SIRA UYARISI: 0026 bu gocun Turkce kolonlarini Ingilizce'ye cevirdi.
-- Bu down 0026'nin down'undan SONRA kosar (yani kolonlar yeniden Turkce
-- adlarina donmus olur). Her iki adi da DROP IF EXISTS ile karsiliyoruz ki
-- hangi noktada durulursa durulsun sema temiz kalsin (D-251/5 idempotent).
--
-- mersis_number DUSURULMEZ: o kolon 0025'ten once vardi (D-251/2, ikiz yasagi
-- geregi 0025 yeni mersis kolonu ACMADI). Yalnizca 0025'in koydugu kisit kalkar.

ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_mersis_no_bicim;
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_kimlik_tamligi_aralik;
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_puan_surum_zorunlu;
DROP INDEX IF EXISTS ix_companies_puan_surumu;

ALTER TABLE companies DROP COLUMN IF EXISTS vergi_dairesi;
ALTER TABLE companies DROP COLUMN IF EXISTS ticaret_sicil_no;
ALTER TABLE companies DROP COLUMN IF EXISTS sicil_dairesi;
ALTER TABLE companies DROP COLUMN IF EXISTS kimlik_tamligi;
ALTER TABLE companies DROP COLUMN IF EXISTS puan_surumu;

-- 0026 down'u atlanmis olabilir: Ingilizce adlari da temizle.
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_mersis_number_format;
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_identity_completeness_range;
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_score_version_required;
DROP INDEX IF EXISTS ix_companies_score_version;

ALTER TABLE companies DROP COLUMN IF EXISTS tax_office;
ALTER TABLE companies DROP COLUMN IF EXISTS trade_registry_number;
ALTER TABLE companies DROP COLUMN IF EXISTS trade_registry_office;
ALTER TABLE companies DROP COLUMN IF EXISTS identity_completeness;
ALTER TABLE companies DROP COLUMN IF EXISTS score_version;
