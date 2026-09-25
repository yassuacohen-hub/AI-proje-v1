-- Migration 0019 down: Admin MFA tablolarını geri al

DROP TABLE IF EXISTS admin_mfa_login_tokens;
DROP TABLE IF EXISTS admin_mfa_setup_tokens;
DROP TABLE IF EXISTS admin_mfa;