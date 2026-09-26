-- Migration 0016 down: users.last_login kolonu
-- Migration 0016_users_last_login.sql'in tersidir

DROP INDEX IF EXISTS idx_users_last_login;
ALTER TABLE users DROP COLUMN IF EXISTS last_login;