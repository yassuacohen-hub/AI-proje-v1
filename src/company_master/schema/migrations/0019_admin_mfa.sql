-- Migration 0019: Admin MFA tablosu
-- TOTP tabanlı MFA (Time-based One-Time Password) için admin_mfa tablosu

CREATE TABLE IF NOT EXISTS admin_mfa (
    admin_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    secret_key TEXT NOT NULL,                    -- TOTP secret (base32, encrypted in prod)
    enabled BOOLEAN NOT NULL DEFAULT FALSE,       -- MFA aktif mi
    backup_codes TEXT,                            -- JSON array of backup codes (hashed)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMPTZ
);

-- MFA setup token geçici tablosu (1 dakika geçerli)
CREATE TABLE IF NOT EXISTS admin_mfa_setup_tokens (
    token_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    secret_key TEXT NOT NULL,                     -- Plaintext secret (setup sırasında)
    mfa_token TEXT NOT NULL UNIQUE,               -- Setup token (1 dk geçerli)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE
);

-- MFA login token geçici tablosu (5 dakika geçerli) - B-02
CREATE TABLE IF NOT EXISTS admin_mfa_login_tokens (
    token_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    mfa_token TEXT NOT NULL UNIQUE,               -- Login token (5 dk geçerli)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE
);

-- Indexler
CREATE INDEX IF NOT EXISTS idx_admin_mfa_setup_tokens_admin ON admin_mfa_setup_tokens(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_mfa_setup_tokens_token ON admin_mfa_setup_tokens(mfa_token);
CREATE INDEX IF NOT EXISTS idx_admin_mfa_login_tokens_admin ON admin_mfa_login_tokens(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_mfa_login_tokens_token ON admin_mfa_login_tokens(mfa_token);