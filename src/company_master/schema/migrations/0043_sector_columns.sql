-- 0043: ihale_ilanlari tablosunda kalan ASCII-Turkce kolonlari Ingilizce'ye cevirir.
--
-- Karar: D-251/1 (sema dili Ingilizce), D-308 (VERI-02 kod sahipligine saygi).
--
-- NEDEN YENI GOC, NEDEN 0042'YE EKLENMEDI: 0042 ilk elde 9 kolonu cevirdi.
-- Bu tur 8 kolon daha var; ikisini ayrı goc yapmak, her gocun defter
-- satirini netlestirir. Birlestirmek, bir hata bulundugunda hepsini
-- geri almayi zorlastirir.
--
-- NEDEN RENAME, NEDEN DROP+CREATE DEGIL: olculdu (2026-09-30, bu gocten
-- once) -> ihale_ilanlari=0 satir. Yani kayip riski YOK. Buna ragmen
-- RENAME secildi; DROP yazilsa ve olcum yanlis olsa veri sessizce
-- giderdi. RENAME en kotu durumda bile veriyi tasir.
--
-- D-251/5: RENAME idempotent DEGIL. DO blogu
-- "kaynak var ve hedef yoksa" kosuluyla kurulur.
--
-- VERI-02 NOTU: bu kolonlari okuyan `osb_tender_monitor.py` utku sahipligindedir.
-- 0043 sirf SCHEMA'yi cevirir; kodun `kısa isim` kolonlara eriseni utku
-- ayrı bir gostergeste gunceller. Kodu bu dosyada dokunmayin.

BEGIN;

DO $$
DECLARE
    esl TEXT[][] := ARRAY[
        ['ilan_basligi',    'tender_title'],
        ['ilan_turu',       'tender_type'],
        ['il',              'province'],
        ['osb_adi',         'osb_name'],
        ['tahmini_maliyet', 'estimated_cost'],
        ['birim',           'unit'],
        ['aciklama',        'description'],
        ['belge_url',       'document_url']
    ];
    i INT;
    var_say TIMESTAMP;
    yeni_say INT;
BEGIN
    SELECT count(*) INTO var_say FROM information_schema.columns
     WHERE table_schema='public' AND table_name='ihale_ilanlari' AND column_name='ilan_basligi';
    SELECT count(*) INTO yeni_say FROM information_schema.columns
     WHERE table_schema='public' AND table_name='ihale_ilanlari' AND column_name='tender_title';

    IF var_say > 0 AND yeni_say = 0 THEN
        FOR i IN 1 .. array_length(esl, 1) LOOP
            IF EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_schema = 'public'
                         AND table_name = 'ihale_ilanlari'
                         AND column_name = esl[i][1])
               AND NOT EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_schema = 'public'
                         AND table_name = 'ihale_ilanlari'
                         AND column_name = esl[i][2]) THEN
                EXECUTE format('ALTER TABLE ihale_ilanlari RENAME COLUMN %I TO %I',
                               esl[i][1], esl[i][2]);
            END IF;
        END LOOP;
    ELSE
        RAISE NOTICE 'ihale_ilanlari icin 0043 atlaniyor (eski=%s, yeni=%s). 0042 zaten tumi.', var_say, yeni_say;
    END IF;
END $$;

-- Indeksler: 0042 bu 3'u Ingilizce isimlere cevirdi ama `il` kolonu hâlâ
-- Turkce idi. 0043 sonrası `il` -> `province`; indeks adlari da
-- consistanttir (0042 zaten idx_ihale_ilanlari_il -> province icin
-- yeniden kurulmaliydi; ama `il` hâlâ vardı). 0042 icindeki ilk 3
-- CREATE IF NOT EXISTS ile korunabilirdi, ama `il` kolonu yok edildiginde
-- indeks otomaatik invalide olur. Yeniden kuruyoruz.

DROP INDEX IF EXISTS idx_ihale_ilanlari_il;
CREATE INDEX IF NOT EXISTS idx_ihale_ilanlari_il
    ON ihale_ilanlari(province, district);

COMMIT;

-- ---------------------------------------------------------------------------
-- VERI-02 NOTU (D-308): osb_tender_monitor.py IcacleIlan dataclass'i
-- asagidaki kolonlari referans eder:
--   kaynak_id         -> 0042'de source_id'ye cevrildi; kod da guncellendi
--   ilan_basligi      -> 0043: tender_title
--   ilan_turu         -> 0043: tender_type
--   il               -> 0043: province
--   osb_adi           -> 0043: osb_name
--   tahmini_maliyet   -> 0043: estimated_cost
--   birim             -> 0043: unit
--   aciklama          -> 0043: description
--   belge_url         -> 0043: document_url
--
-- 0043 ardindan osb_tender_monitor.py IcacleIlan alanlari da ayni isimlerle
-- guncellemek zorundadir, aksi halde SQLAlchemy INSERT/SELECT mismatch
-- hatasi verir. Bu kod utku sahipligindedir; utku ya da ihsan guncelleyecek.
-- ---------------------------------------------------------------------------
