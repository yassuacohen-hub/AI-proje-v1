-- 0036 geri alma: iki olu kolonu semaya geri ekler.
--
-- DIKKAT — ICERIK GERI GELMEZ, sadece kolon geri gelir:
--   nace_codes.is_manufacturing : degeri her zaman SABIT false oldugu icin
--     DEFAULT FALSE ile geri gelmesi eski durumun birebir aynisidir (bilgi
--     kaybi yok; zaten sifir bilgi tasiyordu -- D-249).
--   companies.nace_name : 52 satirlik OSB sektor etiketi geri YAZILMAZ.
--     Kaynagi ham arsivdir ve orada durur (D-246/4). Geri doldurmak gerekirse:
--       UPDATE companies c SET nace_name = s.sektor
--       FROM (SELECT DISTINCT company_id,
--                    nullif(btrim(raw_payload->>'sektor'),'') AS sektor
--             FROM source_records WHERE company_id IS NOT NULL) s
--       WHERE s.company_id = c.company_id AND s.sektor IS NOT NULL;
--     Bu 47 satiri geri getirir; kalan 5'in kaynagi yoktur (olculdu).

BEGIN;

ALTER TABLE nace_codes ADD COLUMN IF NOT EXISTS is_manufacturing BOOLEAN DEFAULT FALSE;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS nace_name TEXT;

COMMIT;
