-- Migration 0020 down: B-04 hesap kilitleme kolonlarini geri al

ALTER TABLE users DROP COLUMN IF EXISTS locked_until;
ALTER TABLE users DROP COLUMN IF EXISTS failed_login_attempts;
