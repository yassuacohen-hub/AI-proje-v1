-- Migration 0017 down: user_activity_log
-- Migration 0017_user_activity_log.sql'in tersidir

DROP INDEX IF EXISTS idx_activity_tip_zaman;
DROP INDEX IF EXISTS idx_activity_user_zaman;
DROP TABLE IF EXISTS user_activity_log;