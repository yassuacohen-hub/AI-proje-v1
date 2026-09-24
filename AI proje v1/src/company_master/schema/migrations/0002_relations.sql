-- Migration 0002: Şirket ilişki tabloları
-- Kaynak: V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md §3.2–§3.11
-- Ön koşul: 0001_core.sql (companies, osbs, sources)

-- §3.2 Aynı şirketin farklı kaynaklardaki adları
CREATE TABLE IF NOT EXISTS company_names (
    company_name_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    name_type       TEXT CHECK (name_type IN ('legal', 'trade', 'brand', 'source_variant', 'historical')),
    source_id       UUID REFERENCES sources(source_id),
    normalized_name TEXT,
    valid_from      DATE,
    valid_to        DATE,
    confidence      NUMERIC(5,2)
);

CREATE INDEX IF NOT EXISTS idx_company_names_company ON company_names(company_id);
CREATE INDEX IF NOT EXISTS idx_company_names_normalized_trgm ON company_names USING gin (normalized_name gin_trgm_ops);

-- §3.3 VKN, MERSİS ve diğer kimlikler
CREATE TABLE IF NOT EXISTS company_identifiers (
    identifier_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id       UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    identifier_type  TEXT NOT NULL,  -- vkn, mersis, ticaret_sicil, ...
    identifier_value TEXT NOT NULL,
    source_id        UUID REFERENCES sources(source_id),
    confidence       NUMERIC(5,2),
    verified_at      TIMESTAMPTZ,
    UNIQUE (identifier_type, identifier_value)
);

CREATE INDEX IF NOT EXISTS idx_company_identifiers_company ON company_identifiers(company_id);

-- §3.4 Çoklu fiziksel lokasyon desteği
CREATE TABLE IF NOT EXISTS company_locations (
    location_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id         UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    location_type      TEXT CHECK (location_type IN
        ('headquarters', 'factory', 'branch', 'warehouse', 'office', 'workshop', 'unknown')),
    address_line       TEXT,
    district           TEXT,
    neighborhood       TEXT,
    city               TEXT,
    postal_code        TEXT,
    latitude           NUMERIC(9,6),
    longitude          NUMERIC(9,6),
    geocode_confidence NUMERIC(5,2),
    osb_id             UUID REFERENCES osbs(osb_id),
    is_primary         BOOLEAN DEFAULT FALSE,
    source_id          UUID REFERENCES sources(source_id),
    verified_at        TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_company_locations_company ON company_locations(company_id);
CREATE INDEX IF NOT EXISTS idx_company_locations_osb ON company_locations(osb_id);

-- §3.7 NACE kod master tablosu (hiyerarşik, MVP'de NACE C öncelikli)
CREATE TABLE IF NOT EXISTS nace_codes (
    nace_code        TEXT PRIMARY KEY,
    version          TEXT,
    level            INTEGER,
    parent_code      TEXT REFERENCES nace_codes(nace_code),
    title            TEXT,
    sector_group     TEXT,
    is_manufacturing BOOLEAN DEFAULT FALSE
);

-- §3.6 Şirket–NACE ilişkisi (çoklu faaliyet destekli)
CREATE TABLE IF NOT EXISTS company_industries (
    company_industry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    nace_code           TEXT REFERENCES nace_codes(nace_code),
    nace_version        TEXT,
    nace_level          INTEGER,
    is_primary          BOOLEAN DEFAULT FALSE,
    source_id           UUID REFERENCES sources(source_id),
    confidence          NUMERIC(5,2),
    verified_at         TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_company_industries_company ON company_industries(company_id);
CREATE INDEX IF NOT EXISTS idx_company_industries_nace ON company_industries(nace_code);

-- §3.10 Hiyerarşik ürün ağacı
CREATE TABLE IF NOT EXISTS product_categories (
    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id   UUID REFERENCES product_categories(category_id),
    name        TEXT NOT NULL,
    level       INTEGER
);

-- §3.9 Ürün master tablosu
CREATE TABLE IF NOT EXISTS products (
    product_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_name TEXT NOT NULL,
    category_id    UUID REFERENCES product_categories(category_id),
    description    TEXT,
    product_status TEXT
);

-- §3.8 Şirket–ürün ilişkisi
-- Not: evidence_id FK'si 0003_intelligence.sql'de evidence tablosu oluştuktan sonra eklenir.
CREATE TABLE IF NOT EXISTS company_products (
    company_product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id         UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    product_id         UUID REFERENCES products(product_id),
    relation_type      TEXT CHECK (relation_type IN
        ('manufacturer', 'supplier', 'distributor', 'reseller', 'service_provider', 'integrator', 'unknown')),
    evidence_id        UUID,  -- FK: 0003'te eklenir
    confidence         NUMERIC(5,2),
    first_seen_at      TIMESTAMPTZ,
    last_seen_at       TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_company_products_company ON company_products(company_id);
CREATE INDEX IF NOT EXISTS idx_company_products_product ON company_products(product_id);

-- §3.11 Kurumsal iletişim bilgileri (öncelik kurumsaldır)
CREATE TABLE IF NOT EXISTS company_contacts (
    contact_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    contact_type TEXT CHECK (contact_type IN
        ('main_phone', 'sales_phone', 'general_email', 'sales_email', 'info_email', 'website', 'social_profile')),
    value        TEXT NOT NULL,
    is_public    BOOLEAN DEFAULT FALSE,
    source_id    UUID REFERENCES sources(source_id),
    confidence   NUMERIC(5,2),
    verified_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_company_contacts_company ON company_contacts(company_id);
