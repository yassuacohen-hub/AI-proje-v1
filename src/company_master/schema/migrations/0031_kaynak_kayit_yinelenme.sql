-- 0031: source_records yinelenme temizligi + UNIQUE(source_id, external_id)
--
-- URUN SAHIBI KARARI (D-261): "content_hash uretimini duzelt, (source_id,
-- external_id) UNIQUE kisiti koy, 3880 kopyayi sil. Kisit olmadan her kazima
-- tabloyu yeniden sisirir."
--
-- KOK NEDEN (scripts/ingest_ivedik_baskent.py):
--   _content_hash() TUM ham kaydi hashliyordu. Kayitta `cekilme_tarihi` var ve
--   mikrosaniyeli. Ayni firma her kosuda YENI hash uretip YENI satir aciyordu.
--   ivedik.org.tr: 3134 satir -> 14 benzersiz firma (3120 kopya).
--   baskentosb.org.tr: slug alani None -> external_id NULL -> 761 satir kimliksiz.
--   Kod tarafi bu gocle birlikte duzeltildi (KIMLIK_ALANLARI + _external_id).
--
-- SILME GUVENLIGI OLCUMU (2026-09-28, canli DB):
--   kopya grubu sayisi                    : 14
--   icerigi FARKLI olan grup              : 0   -> silinen satirlar birebir kopya
--   birden fazla firmaya bagli grup       : 0   -> bag bilgisi kaybolmuyor
--   silinecek satir                       : 3120
--   Yani veri kaybi YOK; ayni icerigin fazla kopyalari dusuyor.
--
-- ILK DENEMEDE PATLADI, OLCUM EKSIKTI (aciktan yazilir):
--   Ilk surum kazanani yalnizca source_records.company_id yonune bakarak sectgi.
--   Canli DB `companies.source_record_id` FK'sini gosterdi: firma da kendisini
--   doguran kaynak satirina isaret ediyor. O satir silinince FK ihlali olustu,
--   islem geri alindi, veri bozulmadi. TERS BAG olculdu:
--     her kopya grubunda companies tarafindan referans alinan satir : tam 1
--     birden fazla referansli satiri olan grup                      : 0
--   Bu yuzden kazanan sirasinin ILK olcutu artik "companies bu satira
--   isaret ediyor mu". Boylece silinen hicbir satir referansli degil.
--
-- NEDEN 3880 DEGIL 3120:
--   3880'in 760'i baskentosb'un external_id'si NULL oldugu icin "benzersiz 0"
--   gorunuyordu. NULL kimlikle hangi satirin kopya oldugu BILINEMEZ; o satirlar
--   SILINMEZ. Kaziyici artik auto: kimlik uretiyor, yeniden yukleme sonrasi
--   gercek kopya sayisi olculecek (BORC-EXTID-01).
--
-- KISIT external_id NULL olan satirlari ETKILEMEZ: PostgreSQL'de UNIQUE, NULL'lari
-- birbirinden farkli sayar. Bu yuzden mevcut 761 baskentosb satiri kisiti
-- ihlal etmez; koruma da saglamaz. Koruma ancak kimlik uretilince baslar.
--
-- Idempotent: DELETE tekrar kosarsa 0 satir siler; kisit IF NOT EXISTS ile.
-- Geri alma: down/0031_kaynak_kayit_yinelenme.down.sql (kisiti dusurur;
-- SILINEN SATIRLAR GERI GELMEZ, ham JSONL dosyalarindan yeniden yuklenir).

-- 1) Her (source_id, external_id) grubunda TEK satir kalir.
--    Kazanan sirasi (onem sirasiyla):
--      a) companies.source_record_id bu satira isaret ediyor mu -> FK kirilmasin
--      b) source_records.company_id dolu mu                     -> bag korunsun
--      c) en eski collected_at                                  -> ilk gozlem
--      d) source_record_id                                       -> esitlik bozucu
--    D-254 dersi: kazanan secimi bayat/ilgisiz kolona degil, korunmasi gereken
--    bilgiye gore yapilir.
DELETE FROM source_records sr
WHERE sr.external_id IS NOT NULL
  AND sr.external_id <> ''
  AND sr.source_record_id <> (
      SELECT k.source_record_id
      FROM source_records k
      WHERE k.source_id = sr.source_id
        AND k.external_id = sr.external_id
      ORDER BY
          (NOT EXISTS (SELECT 1 FROM companies c
                       WHERE c.source_record_id = k.source_record_id)),
          (k.company_id IS NULL),
          k.collected_at ASC NULLS LAST,
          k.source_record_id ASC
      LIMIT 1
  );

-- 2) Kisit: ayni kaynakta ayni dis kimlik iki kez yazilamaz.
ALTER TABLE source_records
    ADD CONSTRAINT source_records_source_external_uniq
    UNIQUE (source_id, external_id);
