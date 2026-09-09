-- Migration 0004: MVP Faz 1.2 genişletme tabloları (PostgreSQL sürümü)
-- Kaynak: V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md §3.X
-- Karar referansı: V10/10_ankara_osb_sentez Karar 5
-- FK hedefi: companies(company_id)

CREATE TABLE IF NOT EXISTS company_capabilities (
    capability_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    capability_type TEXT NOT NULL CHECK (capability_type IN ('product', 'service', 'process', 'technology')),
    title           TEXT NOT NULL,
    description     TEXT,
    nace_code       TEXT,
    source          TEXT NOT NULL DEFAULT 'manual',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_capabilities_company ON company_capabilities(company_id);
CREATE INDEX IF NOT EXISTS idx_capabilities_type ON company_capabilities(capability_type);
CREATE INDEX IF NOT EXISTS idx_capabilities_nace ON company_capabilities(nace_code);

CREATE TABLE IF NOT EXISTS certifications (
    certification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id       UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    cert_type        TEXT NOT NULL,
    cert_number      TEXT,
    issued_by        TEXT,
    issued_date      DATE,
    expiry_date      DATE,
    is_valid         BOOLEAN NOT NULL DEFAULT TRUE,
    source           TEXT NOT NULL DEFAULT 'manual',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_certifications_company ON certifications(company_id);
CREATE INDEX IF NOT EXISTS idx_certifications_type ON certifications(cert_type);
CREATE INDEX IF NOT EXISTS idx_certifications_valid ON certifications(is_valid);

CREATE TABLE IF NOT EXISTS key_personnel (
    personnel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    full_name    TEXT NOT NULL,
    position     TEXT NOT NULL,
    is_public    BOOLEAN NOT NULL DEFAULT FALSE,
    source       TEXT NOT NULL DEFAULT 'manual',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_personnel_company ON key_personnel(company_id);
CREATE INDEX IF NOT EXISTS idx_personnel_public ON key_personnel(is_public);