-- SEMA-DENETIM-01: Kodda sorgulanan ama semada hic olusturulmamis 5 tablo.
-- Tespit: kaynak taramasi (FROM/JOIN/INSERT INTO) vs DB katalogu karsilastirmasi.
-- Hepsi IF NOT EXISTS; migration zinciri tekrar calistirilabilir.

-- 1) audit_logs <- src/company_master/logging/audit_logger.py (AUDIT_LOG_SQL ile ayni),
--    admin_export.py:71 okuyor. DDL uygulama kodunda gomuluydu, semaya tasindi.
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    level VARCHAR(10) NOT NULL,
    logger_name VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    extra JSONB DEFAULT '{}',
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    ip_address VARCHAR(45),
    action VARCHAR(100),
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    result VARCHAR(20),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_logs(resource_type, resource_id);

-- 2) admin_audit_log <- web_app.py:3202 (INSERT), admin_panel.py:1229 (SELECT).
--    Feature flag toggle gecmisi; audit_logs'tan ayri, admin eylem defteri.
CREATE TABLE IF NOT EXISTS admin_audit_log (
    id BIGSERIAL PRIMARY KEY,
    admin_id VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    target VARCHAR(255),
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admin_audit_action ON admin_audit_log(action, changed_at DESC);

-- 3) entity_matches <- entity_resolution/threshold_optimizer.py:31,44.
--    VKN/unvan esleme sonuclari; threshold optimizasyonu bu tablodan besleniyor.
CREATE TABLE IF NOT EXISTS entity_matches (
    match_id BIGSERIAL PRIMARY KEY,
    source_id VARCHAR(255) NOT NULL,
    target_id VARCHAR(255) NOT NULL,
    similarity_score NUMERIC(5, 4) NOT NULL,
    match_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_entity_matches_type ON entity_matches(match_type, similarity_score);

-- 4) campaign_packages <- paketler.py:192 (packages ile JOIN).
--    Kampanya x paket cok-a-cok baglanti tablosu.
CREATE TABLE IF NOT EXISTS campaign_packages (
    campaign_id VARCHAR(64) NOT NULL,
    package_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (campaign_id, package_id)
);

-- 5) api_usage_daily <- admin_kpi.py:107,113,307. Gunluk API istek sayaci.
CREATE TABLE IF NOT EXISTS api_usage_daily (
    date DATE NOT NULL,
    tier VARCHAR(32) NOT NULL DEFAULT 'unknown',
    endpoint VARCHAR(255) NOT NULL DEFAULT '',
    request_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (date, tier, endpoint)
);

CREATE INDEX IF NOT EXISTS idx_api_usage_date ON api_usage_daily(date DESC);
