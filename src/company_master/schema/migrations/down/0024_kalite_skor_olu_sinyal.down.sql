-- Migration 0024 down: skor kolonlarinin DEFAULT 0 varsayilani geri kurulur.
--
-- TAM GERI ALINAMAZ (D-251/4 geregi aciktan yazilir):
-- 0024 sahte 0'lari NULL'a cekti. Hangi satirin NULL'u "0 idi" hangisi
-- "zaten NULL idi" ayrimi kolonda tutulmadi; o bilgi kaybolmustur.
-- Bu down yalnizca SEMAYI eski haline dondurur, VERIYI degil.
-- Veri geri istenirse: yedekten don (D-245).

ALTER TABLE companies
  ALTER COLUMN source_diversity_score   SET DEFAULT 0,
  ALTER COLUMN job_postings_score       SET DEFAULT 0,
  ALTER COLUMN employee_count_score     SET DEFAULT 0,
  ALTER COLUMN job_postings_count       SET DEFAULT 0,
  ALTER COLUMN employee_count_estimate  SET DEFAULT 0;
