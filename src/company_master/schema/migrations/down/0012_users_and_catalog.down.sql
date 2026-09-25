-- Migration 0012 down: Users and catalog tables
-- Migration 0012_users_and_catalog.sql'in tersidir

DROP INDEX IF EXISTS idx_ledger_user;
DROP INDEX IF EXISTS idx_pcat_nace;
DROP INDEX IF EXISTS idx_users_email;
DROP INDEX IF EXISTS idx_users_status;

DROP TABLE IF EXISTS credit_ledger;
DROP TABLE IF EXISTS product_categories;
DROP TABLE IF EXISTS users;