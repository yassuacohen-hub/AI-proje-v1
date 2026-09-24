-- Migration 0016: users.last_login (VERI-ADMIN-LASTLOGIN-MIGRATION-04)
-- Churn zincirinin 1. halkasi: SSOT §11 KK-3 — users tablosunda giris zamani yoktu.
-- Yalnizca sema acar; veri yazmaz (yazma isi API-ADMIN-LASTLOGIN-YAZ-05).
-- Geri alma: 0016_users_last_login.down.sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ NULL;
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login);
