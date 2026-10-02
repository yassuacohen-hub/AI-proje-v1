-- 0049 geri alma: fırsat skoru tablosunu kaldırır.
BEGIN;
DROP TABLE IF EXISTS company_opportunity_scores;
COMMIT;
