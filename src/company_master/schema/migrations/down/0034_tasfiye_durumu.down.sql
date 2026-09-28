-- 0034 geri alma.
--
-- DURUSTLUK NOTU: 'liquidation' isaretlenen satirlarin ONCEKI degeri (9 adet
-- 'active', 14 adet 'unknown') KAYDEDILMEDI. Geri alma hepsini 'unknown' yapar —
-- bu, "bilmiyoruz" demektir ve yanlis 'active' iddiasindan daha durusttur.

BEGIN;

UPDATE companies SET status = 'unknown' WHERE status = 'liquidation';

ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_status_check;
ALTER TABLE companies ADD CONSTRAINT companies_status_check
    CHECK (status IN ('active', 'inactive', 'unknown'));

COMMENT ON COLUMN companies.status IS NULL;

COMMIT;
