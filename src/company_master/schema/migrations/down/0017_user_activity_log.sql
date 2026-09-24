-- Geri alma 0017: user_activity_log (VERI-ADMIN-AKTIVITE-LOG-13)
-- Elle calistirilir; `down/` alt dizini migrate.py glob("*.sql") kapsamina girmez
-- (src/company_master/db/migrate.py:36 — glob recursive degil).
-- Tabloyu dusurmeden once schema_migrations kaydini da sil, yoksa tekrar uygulanmaz.
DROP INDEX IF EXISTS idx_activity_tip_zaman;
DROP INDEX IF EXISTS idx_activity_user_zaman;
DROP TABLE IF EXISTS user_activity_log;
DELETE FROM schema_migrations WHERE filename = '0017_user_activity_log.sql';
