-- Migration 0032: baskentosb.org.tr kimliksiz (external_id IS NULL) eski
-- satirlarin referanslari kimlikli esine TASINIR, sonra eski satirlar silinir.
--
-- veri-gocu: 761 kimliksiz satir silindi, 243 referans + 92 bag tasindi (sema izi yok, olmamali)
--
-- NEDEN:
-- 0031 kopya temizligini (source_id, external_id) uzerinden yapti. baskentosb
-- kazicisi o tarihte external_id URETMIYORDU; NULL'lar UNIQUE kisitina hic
-- girmedi ve temizlikten muaf kaldi. Duzeltilmis kazici yeniden kosturuldu,
-- 482 kimlikli satir yazdi. Simdi ayni firmalar tabloda IKI KEZ duruyor:
-- 761 kimliksiz eski + 482 kimlikli yeni.
--
-- OLCUM (bu goc yazilmadan once, canli DB):
--   kimliksiz eski satir                       : 761
--   ham adi kimlikli yeni satirda da bulunan   : 761  (761/761, istisnasiz)
--   ad eslesmesi TEK yeni satira gidenler      : 757
--   ad eslesmesi IKI yeni satira gidenler      :   4  -> deterministik secim
--   eski satirlardan company_id dolu olan      :  92  -> bag tasinir
--   companies.source_record_id ile isaret edilen: 243 -> referans tasinir
--
-- D-260: silmeden once REFERANS tasinmazsa 243 firmanin kaynak izi kopardi.
-- Bu goc once tasir, sonra siler.

BEGIN;

CREATE TEMP TABLE _bosb_esleme ON COMMIT DROP AS
WITH kaynak AS (
    SELECT source_id FROM sources WHERE source_name = 'baskentosb.org.tr'
),
eski AS (
    SELECT source_record_id, source_id, raw_name, company_id
    FROM source_records
    WHERE source_id IN (SELECT source_id FROM kaynak)
      AND external_id IS NULL
)
SELECT e.source_record_id AS eski_id,
       e.company_id       AS eski_company_id,
       (SELECT y.source_record_id
          FROM source_records y
         WHERE y.source_id = e.source_id
           AND y.external_id IS NOT NULL
           AND y.raw_name = e.raw_name
         -- 4 satirda ad iki yeni kayda gidiyor; en kucuk kimlik secilir ki
         -- goc tekrar kosturulursa ayni sonucu versin (deterministik).
         ORDER BY y.source_record_id
         LIMIT 1) AS yeni_id
FROM eski e;

-- Guvenlik mandali: esi bulunamayan tek bir satir bile varsa goc durur.
-- (Olcumde 0 idi; bu kontrol olcumun bozulmasina karsi.)
DO $$
DECLARE esisiz int;
BEGIN
    SELECT count(*) INTO esisiz FROM _bosb_esleme WHERE yeni_id IS NULL;
    IF esisiz > 0 THEN
        -- Mesajda yuzde isareti KULLANILMAZ: psycopg onu parametre yer
        -- tutucusu sanip dosyayi hic calistirmadan hata veriyor.
        -- Birlestirme (||) hem psql'de hem surucude ayni calisir.
        RAISE EXCEPTION USING MESSAGE =
            'GOC 0032 DURDU: kimlikli esi olmayan satir sayisi = ' || esisiz;
    END IF;
END $$;

-- 1) Firma bagi: yeni satir bagsizsa eskinin bagini devralir.
UPDATE source_records y
   SET company_id = m.eski_company_id
  FROM _bosb_esleme m
 WHERE y.source_record_id = m.yeni_id
   AND y.company_id IS NULL
   AND m.eski_company_id IS NOT NULL;

-- 2) companies.source_record_id referanslari yeni satira tasinir (243 satir).
UPDATE companies c
   SET source_record_id = m.yeni_id
  FROM _bosb_esleme m
 WHERE c.source_record_id = m.eski_id;

-- 3) Artik referanssiz kalan eski kimliksiz satirlar silinir.
DELETE FROM source_records
 WHERE source_record_id IN (SELECT eski_id FROM _bosb_esleme);

COMMIT;
