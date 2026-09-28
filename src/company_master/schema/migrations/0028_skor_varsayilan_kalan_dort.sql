-- GOC-0024-YARIM-01 / D-249 · D-255
--
-- 0024 dokuz skor kolonundan yalnizca BESININ varsayilanini dusurdu. Sebep:
-- o gunun olcumu "farkli deger sayisi = 1" olan kolonlari listeliyordu; kalan
-- dort kolon coklu deger tasidigi icin listeye hic girmedi ve dosyaya
-- yazilmadi. Yani goc uygulanmadi degil, ISI EKSIK YAZILDI. Olcumun kapsami
-- kararin kapsamini belirledi; karar (D-249: "veri yok" != "0 puan") tum skor
-- kolonlari icin gecerliydi.
--
-- Kalan dort kolonun olcumu (2026-09-28, 9412 firma):
--   kolon                  | default | null |  0   | >0   | sahte 0
--   data_freshness_score   |   '0'   |   0  |  707 | 8705 |  707
--   email_validity_score   |   '0'   |   0  | 5455 | 3957 | 5364
--   phone_format_score     |   '0'   |   0  | 1464 | 7948 | 1161
--   social_media_score     |   '0'   |   0  | 4396 | 5016 |  908
--
-- Sahte 0 = besleyen girdi NULL. Gercek 0 = girdi dolu ama sinyal yok
-- (gecersiz e-posta 91, bicimsiz telefon 303, sosyal alan dolu/URL yok 3488).
-- Gercek 0'a DOKUNULMAZ: o bir olcum sonucudur (D-250/4).

ALTER TABLE companies
  ALTER COLUMN data_freshness_score DROP DEFAULT,
  ALTER COLUMN email_validity_score DROP DEFAULT,
  ALTER COLUMN phone_format_score   DROP DEFAULT,
  ALTER COLUMN social_media_score   DROP DEFAULT;

-- Sahte 0 -> NULL. Toplu yazma (D-249/6: satir basina UPDATE yasak).
-- Hepsi idempotent: ikinci kosusta eslesen satir kalmaz.

UPDATE companies SET data_freshness_score = NULL
WHERE data_freshness_score = 0 AND last_verified_at IS NULL;

UPDATE companies SET email_validity_score = NULL
WHERE email_validity_score = 0 AND primary_email IS NULL;

UPDATE companies SET phone_format_score = NULL
WHERE phone_format_score = 0 AND primary_phone IS NULL;

-- social_media girdisi source_records.raw_payload->>'sosyal_medya' icinde.
-- source_record_id NULL olan 3 firma da "girdi yok" sayilir.
UPDATE companies c SET social_media_score = NULL
WHERE c.social_media_score = 0
  AND NOT EXISTS (
    SELECT 1 FROM source_records sr
    WHERE sr.source_record_id = c.source_record_id
      AND sr.raw_payload->>'sosyal_medya' IS NOT NULL
  );
