-- Migration 0015 down: Giriş etkinliği ve arama kaydı tabloları
-- Migration 0015_data_log.sql'in tersidir

DROP INDEX IF EXISTS idx_search_query;
DROP INDEX IF EXISTS idx_search_user;
DROP INDEX IF EXISTS idx_search_ts;
DROP INDEX IF EXISTS idx_search_email;
DROP TABLE IF EXISTS search_events;

DROP INDEX IF EXISTS idx_login_success;
DROP INDEX IF EXISTS idx_login_user;
DROP INDEX IF EXISTS idx_login_ts;
DROP INDEX IF EXISTS idx_login_email;
DROP TABLE IF EXISTS login_events;