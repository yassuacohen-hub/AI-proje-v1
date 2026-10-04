-- Down: Kazıma Denetim Tablolarını Kaldır (0050_scrape_audit_log geri alma)
BEGIN;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'scrape_errors') THEN
    DROP TABLE scrape_errors CASCADE;
  END IF;
END $$;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'scrape_pages') THEN
    DROP TABLE scrape_pages CASCADE;
  END IF;
END $$;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'scrape_audit_log') THEN
    DROP TABLE scrape_audit_log CASCADE;
  END IF;
END $$;

COMMIT;
