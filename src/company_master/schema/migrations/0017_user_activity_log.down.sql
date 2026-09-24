-- Migration 0017 down: user_activity_log geri al (VERI-ADMIN-AKTIVITE-LOG-13)
-- Bu migration 0017_user_activity_log.sql'in tersidir.
DROP INDEX IF EXISTS idx_activity_tip_zaman;
DROP INDEX IF EXISTS idx_activity_user_zaman;
DROP TABLE IF EXISTS user_activity_log;