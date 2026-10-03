-- 0052_website_sablon_kisiti.sql
-- SORUN (canli DB'de olculdu, 2026-10-04, D-238):
--   companies 10123 satir. website_domain: 4677 bos, 2780 gercek, 2666 SABLON:
--     isim.org.tr 2142 · ostimistihdam.com 474 · ostimonline.com 50
--   Kok neden: D-303 kapisi (src/company_master/db/yazma_kapisi.py `kabul()`)
--   var ama HICBIR uretim yolu cagirmiyor (0 cagiran; D-266 deseni). En az 20
--   bagimsiz yazici (etl/normalize.py, scripts/populate_companies_from_payload.py,
--   scripts/backfill_websites.py, ingest_*.py ...) raw_payload->>'web_sitesi'
--   degerini dogrudan kolona yaziyor. Kolonda CHECK/trigger yoktu (olculdu).
--
-- KARAR: kapi veritabanina tasinir (D-246 tek kapi; native kisit > uygulama kodu).
--   BEFORE trigger `kabul()` ile AYNI davranisi yapar: sablon -> NULL (D-249:
--   yokluk NULL'dur, 0 veya sahte deger degil). ETL kirilmaz, sizinti kesilir.
--   Ham deger source_records.raw_payload'da KALIR (kaynak bazli kapatma, alan acik).
--
-- MANDAL: tests/test_website_sablon_kisiti.py — asagidaki desen yazma_kapisi.py
--   SABLON_WEB_DESEN ile birebir esit olmak zorunda (D-211 ikiz degil, D-233).
--   Desen alan adi SINIRINDA eslesir: duz altdizgi `enerjilastik.wixsite.com`,
--   `epsiloncomposite.com`, `aerocomposite.com.tr` (4 gercek satir) yakaliyordu.
--
-- YEDEK (D-244): yedekler/companies_website_sablon_<ts>.jsonl (2666 satir),
--   goc oncesi scripts/website_sablon_yedek.py ile alinir.
--
-- veri-gocu: 2666 satir companies.website_domain sablon -> NULL
--
-- Ilgili Nodlar (D-184/D-218):
--   [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
--   [[Huginn Data Insights/docs/BORC_DEFTERI]] (BORC-SITE-COP-01 kapandi, BORC-YAZMA-KAPISI-01 acik)
--   [[Huginn Data Insights/plans/brief_utku_VERI-WEB-SITESI-ZENGINLESTIR-01]] (dolum gorevi)
--   [[Huginn Data Insights/src/company_master/db/yazma_kapisi.py]]
--   [[Huginn Data Insights/tests/test_website_sablon_kisiti.py]]
--   [[Huginn Data Insights/scripts/website_sablon_yedek.py]]

BEGIN;

CREATE OR REPLACE FUNCTION trg_website_sablon_temizle() RETURNS trigger AS $$
BEGIN
    -- SABLON_WEB_DESEN aynasi (yazma_kapisi.py). sablon_mu() ile ayni.
    IF NEW.website_domain IS NOT NULL AND lower(NEW.website_domain) ~
       '(^|[^a-z0-9-])(isim\.org\.tr|osp\.com\.tr|ostimonline\.com|ostimistihdam\.com|example\.com|site\.com|domain\.com)'
    THEN
        NEW.website_domain := NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS companies_website_sablon ON companies;
CREATE TRIGGER companies_website_sablon
    BEFORE INSERT OR UPDATE OF website_domain ON companies
    FOR EACH ROW EXECUTE FUNCTION trg_website_sablon_temizle();

-- Mevcut sizinti: trigger UPDATE'i yakalar, NULL'a ceker (2666 beklenir).
UPDATE companies
   SET website_domain = website_domain
 WHERE website_domain IS NOT NULL
   AND lower(website_domain) ~
       '(^|[^a-z0-9-])(isim\.org\.tr|osp\.com\.tr|ostimonline\.com|ostimistihdam\.com|example\.com|site\.com|domain\.com)';

COMMENT ON COLUMN companies.website_domain IS
    'Firmanin dogrulanmis web alani. Sablon/portal adresleri (SABLON_WEB, '
    'yazma_kapisi.py) trigger ile NULL''a cekilir (goc 0052). Ham deger '
    'source_records.raw_payload->>''web_sitesi'' icinde kalir.';

COMMIT;
