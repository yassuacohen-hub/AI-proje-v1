-- Company Master V1.0 — Ana şema (PostgreSQL 16+)
-- V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md §3 ile uyumlu.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- UUID Primary Key, VKN benzersiz doğrulama alanı
CREATE TABLE IF NOT EXISTS companies (
    company_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legal_name          TEXT NOT NULL,
    trade_name          TEXT,
    company_type        TEXT,  -- AŞ, Ltd vb.
    tax_number          TEXT UNIQUE,  -- VKN (boş olabilir)
    mersis_number       TEXT UNIQUE,  -- MERSİS (boş olabilir)
    establishment_date  DATE,
    status              TEXT DEFAULT 'unknown',  -- active/inactive/unknown
    status_confidence   NUMERIC(5,2),
    employee_count      INTEGER,
    website_domain      TEXT,
    primary_phone       TEXT,
    primary_email       TEXT,
    description         TEXT,
    is_ankara           BOOLEAN DEFAULT FALSE,
    is_osb_member       BOOLEAN DEFAULT FALSE,
    osb_id              UUID,
    nace_validity       TEXT DEFAULT 'unknown',
    quarantine_reason   TEXT,
    data_quality_score  NUMERIC(5,2),
    entity_confidence   NUMERIC(5,2),
    first_seen_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_verified_at    TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- İletişim bilgisi genişletme (Karar 6, 2026-09-01)
ALTER TABLE companies ADD COLUMN web_sitesi TEXT;
ALTER TABLE companies ADD COLUMN vergi_no TEXT;
ALTER TABLE companies ADD COLUMN osb_parsel TEXT;


CREATE INDEX IF NOT EXISTS idx_companies_tax_number ON companies(tax_number);
CREATE INDEX IF NOT EXISTS idx_companies_legal_name_trgm ON companies USING gin (legal_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status);

-- Ham veri tablosu — silinmez, denetim için saklanır
CREATE TABLE IF NOT EXISTS sources (
    source_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name         TEXT NOT NULL,
    source_type         TEXT NOT NULL,  -- government/osb/chamber/company_website/...
    url                 TEXT,
    authority_score     NUMERIC(5,2),
    collection_method   TEXT,
    legal_basis         TEXT,
    active              BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

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


-- OSB master tablosu
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

-- Karantina tablosu (V9 §11.2)
CREATE TABLE IF NOT EXISTS quarantine_firms (
    quarantine_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_payload     JSONB NOT NULL,
    error_reason    TEXT NOT NULL,
    source_id       UUID,
    source_url      TEXT,
    resolved_status BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Ankara OSB master kayıtları
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


-- ============================================
-- MVP Faz 1.2: Genisletilmis Sema (2026-09-01)
-- ============================================
-- 3 yeni tablo: company_capabilities, certifications, key_personnel
-- Karar referansi: V10/10_ankara_osb_sentez Karar 5
-- Amac: OSTIM sektor detayi + Ivedik olcek zenginlestirme

-- Yetenekler tablosu (sirketin sundugu hizmet/urun kategorileri)
CREATE TABLE IF NOT EXISTS company_capabilities (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id      INTEGER NOT NULL,
    capability_type TEXT NOT NULL CHECK(capability_type IN ('product', 'service', 'process', 'technology')),
    title           TEXT NOT NULL,
    description     TEXT,
    nace_code       TEXT,                              -- Iliskili NACE kodu
    source          TEXT NOT NULL DEFAULT 'manual',   -- manual, scrape, api
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_capabilities_company ON company_capabilities(company_id);
CREATE INDEX IF NOT EXISTS idx_capabilities_type ON company_capabilities(capability_type);
CREATE INDEX IF NOT EXISTS idx_capabilities_nace ON company_capabilities(nace_code);

-- Sertifikalar tablosu (ISO 9001, CE, vb.)
CREATE TABLE IF NOT EXISTS certifications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id      INTEGER NOT NULL,
    cert_type       TEXT NOT NULL,                     -- ISO 9001, ISO 14001, CE, vb.
    cert_number     TEXT,
    issued_by       TEXT,              -- Veren kurulus
    issued_date     TEXT,
    expiry_date     TEXT,
    is_valid        INTEGER NOT NULL DEFAULT 1 CHECK(is_valid IN (0, 1)),
    source          TEXT NOT NULL DEFAULT 'manual',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_certifications_company ON certifications(company_id);
CREATE INDEX IF NOT EXISTS idx_certifications_type ON certifications(cert_type);
CREATE INDEX IF NOT EXISTS idx_certifications_valid ON certifications(is_valid);

-- Anahtar personel tablosu (genel mudur, fabrika muduru, vb.)
CREATE TABLE IF NOT EXISTS key_personnel (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id      INTEGER NOT NULL,
    full_name       TEXT NOT NULL,
    position        TEXT NOT NULL,                     -- Genel Mudur, Fabrika Muduru, vb.
    is_public       INTEGER NOT NULL DEFAULT 0 CHECK(is_public IN (0, 1)),  -- KVKK
    source          TEXT NOT NULL DEFAULT 'manual',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_personnel_company ON key_personnel(company_id);
CREATE INDEX IF NOT EXISTS idx_personnel_public ON key_personnel(is_public);
