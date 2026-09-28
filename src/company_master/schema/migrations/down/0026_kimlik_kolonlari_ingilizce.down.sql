-- Migration 0026 down: Ingilizce kolon adlari 0025'teki Turkce adlarina doner.
--
-- Guvenli: 0026 kosarken bes kolonun da dolu satir sayisi 0 olcumlenmisti
-- (dosyanin basligindaki kanit). RENAME veri tasimaz, yalnizca ad degistirir.
-- D-251/5: RENAME idempotent degil; DO blogu "hedef zaten varsa atla" kurar.

BEGIN;

DO $$
DECLARE
    -- Ingilizce -> Turkce (0026'nin tersi)
    esleme TEXT[][] := ARRAY[
        ['tax_office',            'vergi_dairesi'],
        ['trade_registry_number', 'ticaret_sicil_no'],
        ['trade_registry_office', 'sicil_dairesi'],
        ['identity_completeness', 'kimlik_tamligi'],
        ['score_version',         'puan_surumu']
    ];
    i INT;
BEGIN
    FOR i IN 1 .. array_length(esleme, 1) LOOP
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'companies'
              AND column_name = esleme[i][1]
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'companies'
              AND column_name = esleme[i][2]
        ) THEN
            EXECUTE format(
                'ALTER TABLE companies RENAME COLUMN %I TO %I',
                esleme[i][1], esleme[i][2]
            );
        END IF;
    END LOOP;
END $$;

-- Ingilizce kisit/indeks adlari dusurulur, 0025'in Turkce olanlari geri kurulur.
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_mersis_number_format;
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_identity_completeness_range;
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_score_version_required;
DROP INDEX IF EXISTS ix_companies_score_version;

ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_mersis_no_bicim;
ALTER TABLE companies ADD CONSTRAINT companies_mersis_no_bicim
    CHECK (mersis_number IS NULL OR mersis_number ~ '^[0-9]{16}$');

ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_kimlik_tamligi_aralik;
ALTER TABLE companies ADD CONSTRAINT companies_kimlik_tamligi_aralik
    CHECK (kimlik_tamligi IS NULL OR (kimlik_tamligi >= 0 AND kimlik_tamligi <= 10));

ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_puan_surum_zorunlu;
ALTER TABLE companies ADD CONSTRAINT companies_puan_surum_zorunlu
    CHECK (kimlik_tamligi IS NULL OR puan_surumu IS NOT NULL);

CREATE INDEX IF NOT EXISTS ix_companies_puan_surumu
    ON companies (puan_surumu) WHERE kimlik_tamligi IS NOT NULL;

COMMIT;
