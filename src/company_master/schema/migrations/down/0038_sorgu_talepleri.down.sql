-- 0038 geri alma.
-- DIKKAT: tablo dusurulurse musteri talep GECMISI de gider. Bu geri alma
-- yalnizca goc henuz uretim verisi almadan once guvenlidir.

BEGIN;

DROP INDEX IF EXISTS ix_sorgu_talepleri_company;
DROP INDEX IF EXISTS ix_sorgu_talepleri_acik;

DROP TABLE IF EXISTS sorgu_talepleri;

COMMIT;
