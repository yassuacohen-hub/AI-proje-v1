-- 0044: ihale/tender tablolarında kalan Türkçe kolon ve eksik kolon düzeltmeleri.
--
-- Karar: D-251/1 (sema dili Ingilizce), D-308 (VERI-02 kod sahipligi saygisi).
--
-- NEDEN YENI GOC: 0042 ve 0043 asil kolonlari cevirdi. Bu goc:
--   1) ihale_kaynaklari.isim -> name (Ingilizce sema kurali)
--   2) ihale_ilanlari.cekilme_tarihi kolonu eklenir (kod tarafindan kullaniliyor)
--   3) olculdu (2026-09-30) -> ihale_kaynaklari=0, ihale_ilanlari=0 satir -> kayip riski YOK
--
-- NEDEN RENAME/DROP+CREATE DEGIL: veri YOK. DROP yazilsa ve olcum
-- yanlis olsa veri sessizce giderdi. RENAME/ADD en kotu durumda bile veriyi tasir.
--
-- MANDAL: tests/test_goc_defteri.py test_sema_dili_ingilizce bu kolonlari yakalar.
--
-- DUSEN IZ: cekilme_tarihi kolonu 0045'te crawled_at olarak yeniden adlandirildi.
-- dusen-iz: ihale_ilanlari.cekilme_tarihi
--
-- veri-gocu: isim->name RENAME, cekilme_tarihi eklendi (sonra 0045'te crawled_at oldu)
--
-- VERI-02 NOTU: bu degisiklikler osb_tender_monitor.py kodunun calismasi icin SARTTIR.
-- Kod utku sahipligindedir; goc uygulandiktan sonra utku kodu guncelleyecek.

BEGIN;

-- 1) ihale_kaynaklari: isim -> name
DO $$
DECLARE
    var_say INT;
    yeni_say INT;
BEGIN
    SELECT count(*) INTO var_say FROM information_schema.columns
     WHERE table_schema='public' AND table_name='ihale_kaynaklari' AND column_name='isim';
    SELECT count(*) INTO yeni_say FROM information_schema.columns
     WHERE table_schema='public' AND table_name='ihale_kaynaklari' AND column_name='name';

    IF var_say > 0 AND yeni_say = 0 THEN
        EXECUTE 'ALTER TABLE ihale_kaynaklari RENAME COLUMN isim TO name';
    ELSE
        RAISE NOTICE 'ihale_kaynaklari icin isim->name atlaniyor (eski=%s, yeni=%s).', var_say, yeni_say;
    END IF;
END $$;

-- 2) ihale_ilanlari: cekilme_tarihi kolonu ekle (kod tarafindan kullaniliyor)
-- dusen-iz: ihale_ilanlari.cekilme_tarihi (0045'te crawled_at olarak yeniden adlandirildi)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                     AND table_name = 'ihale_ilanlari'
                     AND column_name = 'cekilme_tarihi')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns
                     WHERE table_schema = 'public'
                       AND table_name = 'ihale_ilanlari'
                       AND column_name = 'crawled_at') THEN
        ALTER TABLE ihale_ilanlari ADD COLUMN cekilme_tarihi TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;
END $$;

COMMIT;