-- Migration 0020: B-04 hesap kilitleme kolonlari
-- web_app.py::api_admin_login_post basarili sifre dogrulamasindan sonra
-- `UPDATE users SET last_login=NOW(), failed_login_attempts=0, locked_until=NULL`
-- calistiriyor; kolonlar yoktu -> HTTP 500 (UndefinedColumn), login hep basarisiz.

ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMPTZ;
