-- Migration 0016 down: users.last_login geri al (VERI-ADMIN-LASTLOGIN-MIGRATION-04)
DROP INDEX IF EXISTS idx_users_last_login;
ALTER TABLE users DROP COLUMN IF EXISTS last_login;