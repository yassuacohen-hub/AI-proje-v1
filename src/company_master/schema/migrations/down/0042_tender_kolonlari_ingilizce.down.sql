-- Migration 0042 down: ihale/tender şema İngilizce kolon adlarına çevrilerek düzeltilir

-- 1) ihale_kaynaklari
DO $$
DECLARE
    esleme TEXT[][] := ARRAY[
        ['source_id', 'kaynak_id'],
        ['is_active', 'aktif']
    ];
    i INT;
BEGIN
    FOR i IN 1 .. array_length(esleme, 1) LOOP
        IF EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                     AND table_name = 'ihale_kaynaklari'
                     AND column_name = esleme[i][1])
          AND NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                     AND table_name = 'ihale_kaynaklari'
                     AND column_name = esleme[i][2]) THEN
            EXECUTE format('ALTER TABLE ihale_kaynaklari RENAME COLUMN %I TO %I',
                           esleme[i][1], esleme[i][2]);
        END IF;
    END LOOP;
END $$;

-- 2) ihale_ilgilendirme_alanlari
DO $$
DECLARE
    esleme TEXT[][] := ARRAY[
        ['source_id', 'kaynak_id'],
        ['source_field_code', 'kaynak_alan_kodu'],
        ['is_active', 'aktif']
    ];
    i INT;
BEGIN
    FOR i IN 1 .. array_length(esleme, 1) LOOP
        IF EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                     AND table_name = 'ihale_ilgilendirme_alanlari'
                     AND column_name = esleme[i][1])
          AND NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                     AND table_name = 'ihale_ilgilendirme_alanlari'
                     AND column_name = esleme[i][2]) THEN
            EXECUTE format('ALTER TABLE ihale_ilgilendirme_alanlari RENAME COLUMN %I TO %I',
                           esleme[i][1], esleme[i][2]);
        END IF;
    END LOOP;
END $$;

-- 3) ihale_ilanlari
DO $$
DECLARE
    esleme TEXT[][] := ARRAY[
        ['source_id', 'kaynak_id'],
        ['source_tender_id', 'kaynak_ilan_id'],
        ['announcement_date', 'duyuru_tarihi'],
        ['question_answer_due', 'soru_cevap_son_tarihi'],
        ['bid_deadline', 'teklif_verme_son_tarihi'],
        ['opening_date', 'acilis_tarihi'],
        ['district', 'ilce'],
        ['status', 'durum'],
        ['source_tender_url', 'kaynak_ilan_url']
    ];
    i INT;
BEGIN
    FOR i IN 1 .. array_length(esleme, 1) LOOP
        IF EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                     AND table_name = 'ihale_ilanlari'
                     AND column_name = esleme[i][1])
          AND NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                     AND table_name = 'ihale_ilanlari'
                     AND column_name = esleme[i][2]) THEN
            EXECUTE format('ALTER TABLE ihale_ilanlari RENAME COLUMN %I TO %I',
                           esleme[i][1], esleme[i][2]);
        END IF;
    END LOOP;
END $$;

-- 4) ihale_katilimcilar
DO $$
DECLARE
    esleme TEXT[][] := ARRAY[
        ['bidder_company_name', 'aday_firma_adi'],
        ['tax_no', 'vergi_no']
    ];
    i INT;
BEGIN
    FOR i IN 1 .. array_length(esleme, 1) LOOP
        IF EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                     AND table_name = 'ihale_katilimcilar'
                     AND column_name = esleme[i][1])
          AND NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                     AND table_name = 'ihale_katilimcilar'
                     AND column_name = esleme[i][2]) THEN
            EXECUTE format('ALTER TABLE ihale_katilimcilar RENAME COLUMN %I TO %I',
                           esleme[i][1], esleme[i][2]);
        END IF;
    END LOOP;
END $$;

-- 5) companies - ikiz kolonları geri al
ALTER TABLE companies ADD COLUMN IF NOT EXISTS adres TEXT;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS nace_name TEXT;

-- İndeksleri Türkçeye geri çevir
DROP INDEX IF EXISTS idx_ihale_ilanlari_tarih;
DROP INDEX IF EXISTS idx_ihale_ilanlari_durum;
DROP INDEX IF NOT EXISTS idx_ihale_ilanlari_il;

CREATE INDEX IF NOT EXISTS idx_ihale_ilanlari_tarih ON ihale_ilanlari(teklif_verme_son_tarihi);
CREATE INDEX IF NOT EXISTS idx_ihale_ilanlari_durum ON ihale_ilanlari(durum);
CREATE INDEX IF NOT EXISTS idx_ihale_ilanlari_il ON ihale_ilanlari(il, ilce);