-- 0025 — Kimlik dosyasi alanlari + puan surumu
-- Karar: D-250, sozlesme K-6. Is: SEMA-VKN-01.
--
-- ustunden-gecen: 0026_kimlik_kolonlari_ingilizce.sql
-- Bu gocun actigi 5 kolon 0026'da Ingilizce'ye cevrildi (D-251/1). Izleri
-- artik bu dosyadaki adlarla aranmaz; guncel adlar icin 0026'ya bakiniz.
-- Dosya gecmis kaydi olarak durur, yeniden calistirilmaz.
-- Gerekce: Kimlik Dosyasi Tamligi agirlik setinde 2.5 puanlik uc alanin kolonu
-- yoktu (vergi_dairesi 0.5 + mersis_no 1.0 + ticaret_sicil_no 1.0). Kolon
-- olmadigi icin bu alanlar hic olculemiyordu; ulasilabilir tavan 6.0'da kalmisti.
--
-- D-249/1 geregi hicbiri DEFAULT almaz: NULL = "toplanmadi", degerli = "toplandi".
-- Dogrulama kolon kisitiyla degil kod tek kapisiyla yapilir (K-1): kimlik_dogrula(),
-- sicil_dogrula(). Kisit sadece kaba bicim tutar.

BEGIN;

-- Kimlik omurgasi alanlari
-- SEMA-IKIZ-01 / D-251: `mersis_no` EKLENMEZ. Semada zaten `mersis_number`
-- (TEXT) var; olculdu, 9412 satirin tamami bos. Yeni kolon acmak ikinci bos
-- ikiz uretirdi. MERSIS alani = companies.mersis_number.
ALTER TABLE companies ADD COLUMN IF NOT EXISTS vergi_dairesi     TEXT;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS ticaret_sicil_no  TEXT;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS sicil_dairesi     TEXT;

-- Kimlik Dosyasi Tamligi (0-10) + agirlik seti surumu.
-- D-250/6: surum olmadan puan bayatlar ve sessizce yanlis kalir.
ALTER TABLE companies ADD COLUMN IF NOT EXISTS kimlik_tamligi    NUMERIC(4,2);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS puan_surumu       TEXT;

-- MERSIS no 16 hanelidir. Bicim kontrolu; gecerlilik kod kapisinda.
-- Mandal: kolon bugun bos, kisit hicbir satiri kirmaz (bkz. _olcum_mersis.py).
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_mersis_no_bicim;
ALTER TABLE companies ADD CONSTRAINT companies_mersis_no_bicim
    CHECK (mersis_number IS NULL OR mersis_number ~ '^[0-9]{16}$');

-- Puan 0-10 araliginda kalir. Disina cikan deger formul hatasidir, veri degil.
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_kimlik_tamligi_aralik;
ALTER TABLE companies ADD CONSTRAINT companies_kimlik_tamligi_aralik
    CHECK (kimlik_tamligi IS NULL OR (kimlik_tamligi >= 0 AND kimlik_tamligi <= 10));

-- Puan varsa surumu de vardir. Surumsuz puan kiyaslanamaz (D-250/6).
ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_puan_surum_zorunlu;
ALTER TABLE companies ADD CONSTRAINT companies_puan_surum_zorunlu
    CHECK (kimlik_tamligi IS NULL OR puan_surumu IS NOT NULL);

-- Surumu bayat olan satirlari panelden ayirmak icin. Kismi indeks: dolu puanlar az.
CREATE INDEX IF NOT EXISTS ix_companies_puan_surumu
    ON companies (puan_surumu) WHERE kimlik_tamligi IS NOT NULL;

COMMIT;
