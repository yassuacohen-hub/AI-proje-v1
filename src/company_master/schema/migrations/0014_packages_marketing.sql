-- DASH-UX-03 Backend: Paket ve Pazarlama tablolari
-- Supabase/PostgreSQL

-- ============================================
-- 0001_paketler.sql
-- ============================================

CREATE TABLE IF NOT EXISTS packages (
    package_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          TEXT NOT NULL,
    description   TEXT DEFAULT '',
    price         NUMERIC(10,2),
    features      JSONB DEFAULT '[]'::jsonb,
    icon          TEXT DEFAULT '',
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_packages_name ON packages(name);
CREATE INDEX IF NOT EXISTS idx_packages_active ON packages(is_active);

-- Firma-Paket ilişkisi
CREATE TABLE IF NOT EXISTS company_packages (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id    UUID NOT NULL REFERENCES companies(company_id),
    package_id    UUID NOT NULL REFERENCES packages(package_id),
    assigned_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status        TEXT DEFAULT 'active',
    UNIQUE(company_id, package_id)
);

CREATE INDEX IF NOT EXISTS idx_cp_company ON company_packages(company_id);
CREATE INDEX IF NOT EXISTS idx_cp_package ON company_packages(package_id);

-- ============================================
-- 0002_pazarlama.sql
-- ============================================

CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          TEXT NOT NULL,
    description   TEXT DEFAULT '',
    status        TEXT DEFAULT 'draft',
    start_date    TIMESTAMPTZ,
    end_date      TIMESTAMPTZ,
    budget        NUMERIC(12,2),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_name ON campaigns(name);

CREATE TABLE IF NOT EXISTS segments (
    segment_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          TEXT NOT NULL,
    description   TEXT DEFAULT '',
    criteria      JSONB DEFAULT '{}'::jsonb,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_segments_active ON segments(is_active);
CREATE INDEX IF NOT EXISTS idx_segments_name ON segments(name);

-- Kampanya-Segment ilişkisi
CREATE TABLE IF NOT EXISTS campaign_segments (
    campaign_id   UUID NOT NULL REFERENCES campaigns(campaign_id),
    segment_id    UUID NOT NULL REFERENCES segments(segment_id),
    PRIMARY KEY (campaign_id, segment_id)
);

-- Segment-Firma ilişkisi
CREATE TABLE IF NOT EXISTS segment_companies (
    segment_id    UUID NOT NULL REFERENCES segments(segment_id),
    company_id    UUID NOT NULL REFERENCES companies(company_id),
    added_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (segment_id, company_id)
);
