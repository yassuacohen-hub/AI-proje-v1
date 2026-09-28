-- 0026 — 0025'in actigi Turkce kolon adlari Ingilizce'ye cevrilir
-- Karar: D-251/1 (sema dili Ingilizce). Is: GOC-DEFTER-01.
--
-- Gerekce: 0025 kimlik alanlarini eklerken 5 Turkce kolon acti
-- (vergi_dairesi, ticaret_sicil_no, sicil_dairesi, kimlik_tamligi, puan_surumu).
-- D-251/1 ayni gun yazildi; goc ondan once uygulanmisti.
--
-- Simdi cevirmenin maliyeti SIFIR, kaniti olculdu:
--   vergi_dairesi=0, ticaret_sicil_no=0, sicil_dairesi=0,
--   kimlik_tamligi=0, puan_surumu=0 dolu satir (9412 firmada).
--   Kodda referans: 0 (entity_resolution.py'deki `vergi_dairesi` DB kolonu
--   degil, ham kayit dataclass alanidir - semaya dokunmaz).
-- Veri yoksa tasima da yok; sadece ad degisir. Bir satir bile dolsaydi
-- bu is D-251/2'deki tasima prosedurune tabi olurdu.
--
-- D-251/5: RENAME idempotent degildir (IF EXISTS yok). DO blogu ile
-- "hedef zaten varsa atla" kurulur; ikinci calisma sessiz gecer.

BEGIN;

DO $$
DECLARE
    -- kaynak -> hedef
    esleme TEXT[][] := ARRAY[
        ['vergi_dairesi',    'tax_office'],
        ['ticaret_sicil_no', 'trade_registry_number'],
        ['sicil_dairesi',    'trade_registry_office'],
        ['kimlik_tamligi',   'identity_completeness'],
        ['puan_surumu',      'score_version']
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

-- Kisit ve indeks adlari da semanin parcasidir; onlar da Ingilizce olur.
-- DROP/ADD ciftiyle yazilir: RENAME CONSTRAINT idempotent degil, kisit
-- tanimi zaten tek satir.
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_mersis_no_bicim;
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_kimlik_tamligi_aralik;
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_puan_surum_zorunlu;
DROP INDEX IF EXISTS ix_companies_puan_surumu;

-- MERSIS no 16 hanelidir. Bicim kontrolu; gecerlilik kod kapisinda (D-246).
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_mersis_number_format;
ALTER TABLE companies ADD CONSTRAINT companies_mersis_number_format
    CHECK (mersis_number IS NULL OR mersis_number ~ '^[0-9]{16}$');

-- Puan 0-10 araliginda kalir. Disina cikan deger formul hatasidir, veri degil.
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_identity_completeness_range;
ALTER TABLE companies ADD CONSTRAINT companies_identity_completeness_range
    CHECK (identity_completeness IS NULL
           OR (identity_completeness >= 0 AND identity_completeness <= 10));

-- Puan varsa surumu de vardir. Surumsuz puan kiyaslanamaz (D-250/6).
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_score_version_required;
ALTER TABLE companies ADD CONSTRAINT companies_score_version_required
    CHECK (identity_completeness IS NULL OR score_version IS NOT NULL);

-- Surumu bayat olan satirlari panelden ayirmak icin. Kismi indeks: dolu puanlar az.
CREATE INDEX IF NOT EXISTS ix_companies_score_version
    ON companies (score_version) WHERE identity_completeness IS NOT NULL;

COMMIT;
