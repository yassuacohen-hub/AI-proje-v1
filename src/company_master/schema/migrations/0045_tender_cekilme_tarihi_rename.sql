-- 0045: ihale_ilanlari.cekilme_tarihi -> crawled_at (Ingilizce sema kurali D-251/1).
--
-- Karar: D-251/1 (sema dili Ingilizce), D-308 (VERI-02 kod sahipligi).
--
-- NEDEN: 0044 cekilme_tarihi ekledi ama Turkce adi test_sema_dili_ingilizce'yi kiriyor.
-- Bu goc adi Ingilizce'ye cevirir.
--
-- NEDEN RENAME: veri YOK (tablo 0 satir). Kayip riski YOK.
--
-- veri-gocu: cekilme_tarihi -> crawled_at RENAME (D-251/1 Ingilizce sema uyumu)

BEGIN;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_schema = 'public'
                 AND table_name = 'ihale_ilanlari'
                 AND column_name = 'cekilme_tarihi')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'ihale_ilanlari'
                   AND column_name = 'crawled_at') THEN
        EXECUTE 'ALTER TABLE ihale_ilanlari RENAME COLUMN cekilme_tarihi TO crawled_at';
    END IF;
END $$;

COMMIT;