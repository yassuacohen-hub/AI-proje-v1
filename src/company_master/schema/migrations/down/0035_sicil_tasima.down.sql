-- 0035 geri alma.
--
-- Geri alma DURUST: goc oncesi olculen deger 0 / 9412 idi (her iki kolon da
-- tamamen bostu). Bu yuzden NULL'a cekmek "onceki durumu bilmiyoruz" degil,
-- "onceki durum buydu" demektir. Ham deger raw_payload'da durdugu icin
-- veri kaybi da yok (D-246/4).

BEGIN;

UPDATE companies
SET trade_registry_number = NULL,
    trade_registry_office = NULL
WHERE trade_registry_number IS NOT NULL
   OR trade_registry_office IS NOT NULL;

COMMENT ON COLUMN companies.trade_registry_number IS NULL;
COMMENT ON COLUMN companies.trade_registry_office IS NULL;

COMMIT;
