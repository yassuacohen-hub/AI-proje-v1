-- D-310: koken geriye donuk dolum (KAHIN 2026-09-29)
-- uretim: 2026-09-30T00:15:46
-- D-309 kolonlari acti ama NULL'di. Bos kolon, hic eklenmis
-- kolondan FARKSIZDIR. Bu adim kokeni baglar.

BEGIN;
UPDATE public.companies c
SET source_name = s."raw_website"
  FROM public.source_records s
  WHERE s."source_record_id" = c.source_record_id
    AND c.source_name IS NULL;

-- collected_at: source_records.collected_at GERCEK toplama
-- zamanidir; once o denenir. O yoksa companies.first_seen_at
-- (kayit olusturulma ani - TAHMIN, acikca isaretlenir).
UPDATE public.companies c
SET collected_at = s."collected_at"
  FROM public.source_records s
  WHERE s."source_record_id" = c.source_record_id
    AND c.collected_at IS NULL
    AND s."collected_at" IS NOT NULL;
UPDATE public.companies
SET collected_at = "first_seen_at"
WHERE collected_at IS NULL
  AND source_record_id IS NULL;

-- Baglanmamis kayitlar ACIKCA isaretlenir (uydurulmaz)
UPDATE public.companies
SET collected_by = 'migration:source_record_id_bos'
WHERE collected_by IS NULL AND source_record_id IS NULL;
COMMIT;
