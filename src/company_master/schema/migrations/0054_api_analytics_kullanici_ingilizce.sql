-- 0054_api_analytics_kullanici_ingilizce.sql
-- SORUN: 0053, api_analytics.kullanici kolonunu Turkce acti; test_sema_dili_ingilizce
-- (D-251/1 mandali) kirmizi. 0053 "uygulandi" diye deftere yazili oldugu icin
-- dosya geriye donup degistirilmez (D-245: gecmis yeniden yazilmaz, uzerine yazilir).
-- Karar: D-359.
--
-- KARAR: RENAME kullanici -> username. Olculdu: 11 satir veri var, tek yazici
-- src/company_master/logging/api_logger.py, okuyucu yok (admin_api_analytics.py,
-- admin_sistem_saglik.py bu kolonu okumuyor). RENAME veri kaybetmez; DROP+CREATE
-- riskli olurdu (D-245).
--
-- D-251/5: RENAME idempotent degildir, DO blogu + information_schema kontroluyle
-- sarildi; ikinci calisma sessiz gecer.
--
-- veri-gocu: RENAME COLUMN icerir, arac (goc_defteri.py) bu izi semadan
-- otomatik cikaramadigi icin IZSIZ gorunur. Elle olculdu: api_analytics
-- tablosunda `username` kolonu var, `kullanici` kolonu yok (2026-10-06).
--
-- Ilgili Nodlar:
--   [[Huginn Data Insights/src/company_master/logging/api_logger.py]]

BEGIN;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_schema = 'public' AND table_name = 'api_analytics'
                 AND column_name = 'kullanici')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_schema = 'public' AND table_name = 'api_analytics'
                 AND column_name = 'username')
    THEN
        ALTER TABLE api_analytics RENAME COLUMN kullanici TO username;
    END IF;
END $$;

COMMIT;

-- DOWN MIGRATION (for reference, not auto-executed)
-- BEGIN;
-- ALTER TABLE api_analytics RENAME COLUMN username TO kullanici;
-- COMMIT;
