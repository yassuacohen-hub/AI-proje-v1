-- Geri alma 0016: users.last_login (VERI-ADMIN-LASTLOGIN-MIGRATION-04)
-- Elle calistirilir; `down/` alt dizini migrate.py glob("*.sql") kapsamina girmez
-- (src/company_master/db/migrate.py:36 — glob recursive degil).
-- Kolonu dusurmeden once schema_migrations kaydini da sil, yoksa tekrar uygulanmaz.
DROP INDEX IF EXISTS idx_users_last_login;
ALTER TABLE users DROP COLUMN IF EXISTS last_login;
DELETE FROM schema_migrations WHERE filename = '0016_users_last_login.sql';
