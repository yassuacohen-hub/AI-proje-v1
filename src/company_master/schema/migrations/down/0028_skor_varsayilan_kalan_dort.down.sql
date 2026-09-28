-- Migration 0028 down: kalan dort skor kolonunun DEFAULT 0 varsayilani geri kurulur.
--
-- TAM GERI ALINAMAZ (0024 down ile ayni gerekce): sahte 0 -> NULL donusumunde
-- "0 idi" bilgisi kolonda saklanmadi. Bu down SEMAYI geri alir, VERIYI degil.
-- Gercek 0'lara 0028 zaten dokunmadigi icin onlar yerinde durur.

ALTER TABLE companies
  ALTER COLUMN data_freshness_score SET DEFAULT 0,
  ALTER COLUMN email_validity_score SET DEFAULT 0,
  ALTER COLUMN phone_format_score   SET DEFAULT 0,
  ALTER COLUMN social_media_score   SET DEFAULT 0;
