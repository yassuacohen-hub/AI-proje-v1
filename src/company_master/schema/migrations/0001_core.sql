-- Migration 0001: Uzantılar ve çekirdek tablolar
-- Company Master V1.0 — PostgreSQL 16+
-- Kaynak: V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md §3.1, §3.5, §3.12, §3.13
-- Not: Karar 6 (2026-09-01) ile companies'e eklenen web_sitesi/vergi_no/osb_parsel
-- sütunları taze kurulumda doğrudan tablo tanımına dahil edilmiştir.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- unvan benzerlik araması (trigram)

-- OSB master tablosu (companies.osb_id FK'si için önce oluşturulur)
CREATE TABLE IF NOT EXISTS osbs (
    osb_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    city            TEXT NOT NULL DEFAULT 'Ankara',
    district        TEXT,
    website         TEXT,
    osb_type        TEXT,
    status          TEXT DEFAULT 'active',
    source_id       UUID,
    verified_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(name, city)
);

-- Ana şirket tablosu: company_id UUID PK, VKN benzersiz doğrulama alanı (§2)
CREATE TABLE IF NOT EXISTS companies (
    company_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legal_name          TEXT NOT NULL,
    trade_name          TEXT,
    company_type        TEXT,  -- AŞ, Ltd vb.
    tax_number          TEXT UNIQUE,  -- VKN (boş olabilir)
    mersis_number       TEXT UNIQUE,  -- MERSİS (boş olabilir)
    establishment_date  DATE,
    status              TEXT DEFAULT 'unknown' CHECK (status IN ('active', 'inactive', 'unknown')),
    status_confidence   NUMERIC(5,2),
    employee_count      INTEGER,
    website_domain      TEXT,
    primary_phone       TEXT,
    primary_email       TEXT,
    description         TEXT,
    is_ankara           BOOLEAN DEFAULT FALSE,
    is_osb_member       BOOLEAN DEFAULT FALSE,
    osb_id              UUID REFERENCES osbs(osb_id),
    nace_validity       TEXT DEFAULT 'unknown',
    quarantine_reason   TEXT,
    data_quality_score  NUMERIC(5,2),
    entity_confidence   NUMERIC(5,2),
    -- Karar 6 (2026-09-01): iletişim/parsel genişletme sütunları
    web_sitesi          TEXT,
    vergi_no            TEXT,
    osb_parsel          TEXT,
    first_seen_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_verified_at    TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_companies_tax_number ON companies(tax_number);
CREATE INDEX IF NOT EXISTS idx_companies_legal_name_trgm ON companies USING gin (legal_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status);
CREATE INDEX IF NOT EXISTS idx_companies_osb ON companies(osb_id);

-- Veri kaynakları (§3.12)
CREATE TABLE IF NOT EXISTS sources (
    source_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name         TEXT NOT NULL,
    source_type         TEXT NOT NULL CHECK (source_type IN
        ('government', 'osb', 'chamber', 'company_website', 'public_registry', 'search_engine', 'manual', 'other')),
    url                 TEXT,
    authority_score     NUMERIC(5,2),
    collection_method   TEXT,
    legal_basis         TEXT,
    active              BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Ham kaynak kayıtları (§3.13) — silinmez, denetim ve yeniden işleme için saklanır
CREATE TABLE IF NOT EXISTS source_records (
    source_record_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id           UUID NOT NULL REFERENCES sources(source_id),
    external_id         TEXT,
    raw_name            TEXT,
    raw_address         TEXT,
    raw_phone           TEXT,
    raw_email           TEXT,
    raw_website         TEXT,
    raw_tax_number      TEXT,
    raw_nace            TEXT,
    raw_payload         JSONB,
    collected_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    content_hash        TEXT
);

CREATE INDEX IF NOT EXISTS idx_source_records_source ON source_records(source_id);
CREATE INDEX IF NOT EXISTS idx_source_records_tax ON source_records(raw_tax_number);

-- Karantina tablosu (V9 §11.2): doğrulanamayan ham kayıtlar
CREATE TABLE IF NOT EXISTS quarantine_firms (
    quarantine_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_payload     JSONB NOT NULL,
    error_reason    TEXT NOT NULL,
    source_id       UUID REFERENCES sources(source_id),
    source_url      TEXT,
    resolved_status BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Ankara OSB master kayıtları (liste sabit değildir, kaynaklarla doğrulanır)
INSERT INTO osbs (name, city, district, osb_type) VALUES
    ('OSTİM OSB', 'Ankara', 'Yenimahalle', 'karma'),
    ('İvedik OSB', 'Ankara', 'Yenimahalle', 'karma'),
    ('ASO 1. OSB', 'Ankara', 'Sincan', 'karma'),
    ('ASO 2-3 OSB', 'Ankara', 'Sincan', 'karma'),
    ('Başkent OSB', 'Ankara', 'Kazan', 'karma'),
    ('HAB OSB (Havaalanı)', 'Ankara', 'Yenimahalle', 'ihtisas'),
    ('Dökümcüler OSB', 'Ankara', 'Sincan', 'ihtisas'),
    ('Anadolu OSB', 'Ankara', 'Sincan', 'karma'),
    ('Polatlı OSB', 'Ankara', 'Polatlı', 'karma')
ON CONFLICT (name, city) DO NOTHING;
