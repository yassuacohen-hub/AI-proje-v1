-- 0044 down: ihale_kaynaklari.name -> isim geri al, ihale_ilanlari zaman kolonunu kaldir.
--
-- Karar: D-251/3 (goc defteri tek anlatici), D-308 (VERI-02 kod sahipligi).
--
-- SIRA NOTU: 0045 down once kosar (crawled_at -> cekilme_tarihi). Bu dosya
-- yine de IKI adi birden dener; cunku 0045 uygulanmamissa kolon cekilme_tarihi,
-- uygulanmissa ve 0045 down atlanmissa crawled_at adinda durur.

BEGIN;

-- 1) ihale_kaynaklari: name -> isim (geri)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_schema='public' AND table_name='ihale_kaynaklari'
                 AND column_name='name')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_schema='public' AND table_name='ihale_kaynaklari'
                 AND column_name='isim') THEN
        EXECUTE 'ALTER TABLE ihale_kaynaklari RENAME COLUMN name TO isim';
    END IF;
END $$;

-- 2) 0044'un ekledigi zaman kolonu (hangi adda durursa) kaldirilir
ALTER TABLE ihale_ilanlari DROP COLUMN IF EXISTS cekilme_tarihi;
ALTER TABLE ihale_ilanlari DROP COLUMN IF EXISTS crawled_at;

COMMIT;
