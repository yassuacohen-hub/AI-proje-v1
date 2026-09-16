-- DATA-LOG-01: Giriş etkinliği ve arama kaydı tablolari
-- SQLite + PostgreSQL uyumlu

-- ============================================
-- login_events
-- ============================================
CREATE TABLE IF NOT EXISTS login_events (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       TEXT,
    email_masked  TEXT NOT NULL,
    ts            TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_masked     TEXT NOT NULL,
    user_agent    TEXT DEFAULT '',
    success       INTEGER NOT NULL DEFAULT 0,
    method        TEXT NOT NULL DEFAULT 'POST',
    path          TEXT NOT NULL DEFAULT '/api/buyer/login',
    error_msg     TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_login_email ON login_events(email_masked);
CREATE INDEX IF NOT EXISTS idx_login_ts ON login_events(ts);
CREATE INDEX IF NOT EXISTS idx_login_user ON login_events(user_id);
CREATE INDEX IF NOT EXISTS idx_login_success ON login_events(success);

-- ============================================
-- search_events
-- ============================================
CREATE TABLE IF NOT EXISTS search_events (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        TEXT,
    email_masked   TEXT NOT NULL,
    ts             TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_masked      TEXT NOT NULL,
    query          TEXT NOT NULL DEFAULT '',
    result_count   INTEGER NOT NULL DEFAULT 0,
    filters        TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_search_email ON search_events(email_masked);
CREATE INDEX IF NOT EXISTS idx_search_ts ON search_events(ts);
CREATE INDEX IF NOT EXISTS idx_search_user ON search_events(user_id);
CREATE INDEX IF NOT EXISTS idx_search_query ON search_events(query);
