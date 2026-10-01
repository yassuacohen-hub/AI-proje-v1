-- 0045 down: ihale_ilanlari.crawled_at -> cekilme_tarihi (0044 halini geri getirir).
--
-- Karar: D-251/3 (goc defteri tek anlatici).
-- NEDEN RENAME: veri kaybi olmaz; DROP yazilsa olcum yanlissa veri sessizce giderdi.

BEGIN;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_schema='public' AND table_name='ihale_ilanlari'
                 AND column_name='crawled_at')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_schema='public' AND table_name='ihale_ilanlari'
                 AND column_name='cekilme_tarihi') THEN
        EXECUTE 'ALTER TABLE ihale_ilanlari RENAME COLUMN crawled_at TO cekilme_tarihi';
    END IF;
END $$;

COMMIT;
