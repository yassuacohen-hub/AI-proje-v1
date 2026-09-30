-- 0042: 0039 (ihale/tender izleyici) Turkce kolon adlarini Ingilizce'ye cevirir.
--
-- Karar: D-251/1 (sema dili Ingilizce). Is: GOC-DEFTER-01 / VERI-02.
--
-- NEDEN YENI GOC, NEDEN 0039 DUZELTILMEDI: 0039 `public.schema_migrations`
-- defterine "uygulandi" olarak yazili. Dosya icerigini geri donup degistirmek
-- defteri yalanci yapardi: defter "uygulandi" derken sema baska bir sey
-- gosterirdi. Gecmis yeniden yazilmaz, uzerine yazilir.
--
-- NEDEN RENAME, NEDEN DROP+CREATE DEGIL: olculdu (2026-09-30, bu gocden
-- once) -> asagidaki 6 tablonun ALISI da 0 satir:
--     ihale_kaynaklari=0, ihale_ilgilendirme_alanlari=0, ihale_ilanlari=0,
--     ihale_katilimcilar=0, ihale_ekler=0, ihale_takip=0
-- Yani kayip riski YOK. Buna ragmen RENAME secildi: DROP yazilsa ve olcum
-- yanlis olsa veri sessizce giderdi. RENAME en kotu durumda bile veriyi tasir.
--
-- MANDAL: `tests/test_goc_defteri.py::test_sema_dili_ingilizce` bu 14 kolonu
-- yakaladi. BILINEN_DIL_BORCU listesi BOS oldugu icin istisna yazilamaz —
-- borc kapanmali. Istisna yazmak borcu gizlemek olurdu.
--
-- D-251/5: RENAME idempotent DEGILDIR (IF EXISTS yok). Asagidaki DO blogu
-- "kaynak var ve hedef yoksa" kosuluyla kurulur; ikinci calisma sessiz gecer.

BEGIN;

-- 1) ihale_kaynaklari  (olculdu: kaynak_id, aktif)
DO $$
DECLARE
    esleme TEXT[][] := ARRAY[
        ['kaynak_id', 'source_id'],
        ['aktif',     'is_active']
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

-- 2) ihale_ilgilendirme_alanlari  (kaynak_id, kaynak_alan_kodu, aktif)
DO $$
DECLARE
    esleme TEXT[][] := ARRAY[
        ['kaynak_id',        'source_id'],
        ['kaynak_alan_kodu', 'source_field_code'],
        ['aktif',            'is_active']
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
            EXECUTE format(
                'ALTER TABLE ihale_ilgilendirme_alanlari RENAME COLUMN %I TO %I',
                esleme[i][1], esleme[i][2]);
        END IF;
    END LOOP;
END $$;

-- 3) ihale_ilanlari — en cok kolon burada (olculdu: 9 Turkce ad)
DO $$
DECLARE
    esleme TEXT[][] := ARRAY[
        ['kaynak_id',               'source_id'],
        ['kaynak_ilan_id',          'source_tender_id'],
        ['duyuru_tarihi',           'announcement_date'],
        ['soru_cevap_son_tarihi',   'question_answer_due'],
        ['teklif_verme_son_tarihi', 'bid_deadline'],
        ['acilis_tarihi',           'opening_date'],
        ['ilce',                    'district'],
        ['durum',                   'status'],
        ['kaynak_ilan_url',         'source_tender_url']
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

-- 4) ihale_katilimcilar  (aday_firma_adi, vergi_no)
DO $$
DECLARE
    esleme TEXT[][] := ARRAY[
        ['aday_firma_adi', 'bidder_company_name'],
        ['vergi_no',       'tax_no']
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

COMMIT;

-- ---------------------------------------------------------------------------
-- Kalan iki borc: ikiz kalinti. Olculdu (2026-09-30, bu gocden ONCE):
--     companies.adres     = 0 dolu satir  (companies.address = 5.798 dolu)
--     companies.nace_name = 0 dolu satir
-- Yani ikisi de BOS kalinti: 0007 `adres`i kurdu, 0027 `address`e cevirdi
-- ama `adres` kolonu geride kaldi; 0036 `nace_name`i dusurdu ama dusurme
-- uygulanmamis. Ikisi de mandali iki ayri yerden kirip duruyordu.
--
-- NEDEN DROP: veri YOK. DROP COLUMN, dolu bir kolonda veri kaybi demektir;
-- burada 0 satiri var, kaybedilecek sey yok. Bir satir bile olsaydi bu
-- satir RENAME'a donusurdu.
--
-- NEDEN RENAME DEGIL: hedef ad (`address`) ZATEN var. Iki kolonu tek
-- ad altinda birlestirmek yerine bos olani dusurmek dogru; tersi veri
-- birlestirmek olurdu.
-- ---------------------------------------------------------------------------
ALTER TABLE companies DROP COLUMN IF EXISTS adres;
ALTER TABLE companies DROP COLUMN IF EXISTS nace_name;

-- Indeksler: RENAME kolon adini degistirir, indeks adi kalir. Tehdidi
-- gormemek icin adlari da Ingilizceye cekiyoruz (0039 bunlari Turkce kurdu).
DROP INDEX IF EXISTS idx_ihale_ilanlari_tarih;
DROP INDEX IF EXISTS idx_ihale_ilanlari_durum;
DROP INDEX IF EXISTS idx_ihale_ilanlari_il;

CREATE INDEX IF NOT EXISTS idx_ihale_ilanlari_tarih ON ihale_ilanlari(bid_deadline);
CREATE INDEX IF NOT EXISTS idx_ihale_ilanlari_durum ON ihale_ilanlari(status);
CREATE INDEX IF NOT EXISTS idx_ihale_ilanlari_il   ON ihale_ilanlari(il, district);

