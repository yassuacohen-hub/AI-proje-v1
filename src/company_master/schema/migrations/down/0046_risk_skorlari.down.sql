-- 0046 geri alma: company_risk_scores tablosunu düşür
--
-- Karar: D-251/5 (RENAME idempotent değil, DROP da idempotent yazılır)
-- veri-gocu: company_risk_scores tablosu DROP (Faz 2 Risk Motoru geri alma)

BEGIN;

DROP TABLE IF EXISTS company_risk_scores;

COMMIT;