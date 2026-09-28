-- KALITE-SKOR-01 / D-249
-- Sorun: 5 skor kolonu DEFAULT 0 yuzunden %100 "dolu" gorunuyordu ama
-- 9412 satirin hepsinde ayni deger vardi. Doluluk != bilgi (D-245).
--
-- Kanit (scripts/_olcum_skor.py):
--   source_diversity_score   farkli deger = 1  (0 x9412)
--   job_postings_score       farkli deger = 1  (0 x9412)
--   employee_count_score     farkli deger = 1  (0 x9412)
--   job_postings_count       farkli deger = 1  (0 x9412)
--   employee_count_estimate  farkli deger = 1  (0 x9412)
--
-- Karar: "veri yok" ile "veri var, degeri 0" ayrilir. Veri yoksa NULL.

ALTER TABLE companies
  ALTER COLUMN source_diversity_score  DROP DEFAULT,
  ALTER COLUMN job_postings_score      DROP DEFAULT,
  ALTER COLUMN employee_count_score    DROP DEFAULT,
  ALTER COLUMN job_postings_count      DROP DEFAULT,
  ALTER COLUMN employee_count_estimate DROP DEFAULT;

-- Besleyen verisi olmayan sinyalleri NULL'a cek.
-- employee_count: 0 dolu kayit -> hepsi NULL
UPDATE companies SET employee_count_score = NULL, employee_count_estimate = NULL;

-- job_postings: 8 firmada veri var, geri kalan NULL
UPDATE companies c SET job_postings_score = NULL, job_postings_count = NULL
WHERE NOT EXISTS (
  SELECT 1 FROM job_postings j WHERE j.company_id = c.company_id
);

-- source_diversity: source_records.company_id uzerinden gercek deger var (0023)
UPDATE companies c SET source_diversity_score = NULL
WHERE NOT EXISTS (
  SELECT 1 FROM source_records sr WHERE sr.company_id = c.company_id
);
