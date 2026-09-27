-- Migration 0021 down: SEMA-DENETIM-01 ile eklenen 5 tabloyu geri al
-- Index'ler tablo ile birlikte dusuyor, ayrica DROP INDEX gerekmez.

DROP TABLE IF EXISTS api_usage_daily;
DROP TABLE IF EXISTS campaign_packages;
DROP TABLE IF EXISTS entity_matches;
DROP TABLE IF EXISTS admin_audit_log;
DROP TABLE IF EXISTS audit_logs;
