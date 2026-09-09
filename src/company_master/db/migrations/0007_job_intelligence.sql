-- 0007_job_intelligence.sql
-- Job Intelligence Module: İş ilanları ve şirket sinyalleri tabloları
-- Tarih: 2026-09-09
-- Bağımlılık: 0001_core.sql (companies, sources, source_records tabloları)

-- ============================================================
-- 1. İş İlanları Ham Veri Tablosu
-- ============================================================
CREATE TABLE IF NOT EXISTS job_postings (
    job_posting_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID REFERENCES companies(company_id),
    source_name         TEXT NOT NULL,                    -- kariyer.net, iskur, company_career, linkedin
    source_url          TEXT NOT NULL,                    -- İlanın orijinal URL'si
    external_id         TEXT,                             -- Kaynağın kendi ID'si
    title               TEXT NOT NULL,                    -- Pozisyon başlığı
    description         TEXT,                             -- İlan açıklaması
    department          TEXT,                             -- Departman (Engineering, Sales, HR, vb.)
    seniority_level     TEXT,                             -- junior, mid, senior, lead, manager, director, c-level
    location_city       TEXT,                             -- Şehir
    location_country    TEXT DEFAULT 'Türkiye',           -- Ülke
    employment_type     TEXT,                             -- full-time, part-time, contract, intern
    remote_type         TEXT,                             -- onsite, hybrid, remote
    technologies        JSONB DEFAULT '[]',               -- ["Python", "AWS", "Kubernetes", "React"]
    salary_min          INTEGER,                          -- Minimum maaş (TL, yıllık)
    salary_max          INTEGER,                          -- Maksimum maaş (TL, yıllık)
    salary_currency     TEXT DEFAULT 'TRY',
    posted_at           TIMESTAMPTZ,                      -- İlan yayın tarihi
    expired_at          TIMESTAMPTZ,                      -- İlan bitiş tarihi
    collected_at        TIMESTAMPTZ DEFAULT NOW(),        -- Toplama tarihi
    content_hash        TEXT,                             -- Değişiklik takibi için hash
    raw_data            JSONB DEFAULT '{}',               -- Ham veri (kaynağa özgü ek alanlar)
    UNIQUE(source_name, external_id)
);

CREATE INDEX IF NOT EXISTS idx_job_postings_company ON job_postings(company_id);
CREATE INDEX IF NOT EXISTS idx_job_postings_source ON job_postings(source_name);
CREATE INDEX IF NOT EXISTS idx_job_postings_posted_at ON job_postings(posted_at);
CREATE INDEX IF NOT EXISTS idx_job_postings_technologies ON job_postings USING GIN (technologies);
CREATE INDEX IF NOT EXISTS idx_job_postings_department ON job_postings(department);
CREATE INDEX IF NOT EXISTS idx_job_postings_seniority ON job_postings(seniority_level);
CREATE INDEX IF NOT EXISTS idx_job_postings_location ON job_postings(location_city, location_country);

-- ============================================================
-- 2. Şirket Sinyalleri Tablosu (Zaman Serisi)
-- ============================================================
CREATE TABLE IF NOT EXISTS company_signals (
    signal_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    signal_type         TEXT NOT NULL,                    -- growth, risk, tech_transformation, investment, geo_expansion, org_change
    signal_subtype      TEXT,                             -- hiring_surge, new_department, cto_hired, tech_modernization, new_city, etc.
    score               NUMERIC(5,2) DEFAULT 0,           -- 0-100 arası sinyal gücü
    confidence          NUMERIC(5,2) DEFAULT 0,           -- 0-100 güven skoru
    evidence            JSONB DEFAULT '{}',               -- Destekleyen veriler: {"job_posting_ids": [...], "date_range": "...", "details": {...}}
    detected_at         TIMESTAMPTZ DEFAULT NOW(),        -- Tespit tarihi
    valid_until         TIMESTAMPTZ,                      -- Sinyalin geçerlilik bitiş tarihi
    metadata            JSONB DEFAULT '{}'                -- Ek metadata
);

CREATE INDEX IF NOT EXISTS idx_company_signals_company ON company_signals(company_id);
CREATE INDEX IF NOT EXISTS idx_company_signals_type ON company_signals(signal_type, signal_subtype);
CREATE INDEX IF NOT EXISTS idx_company_signals_detected ON company_signals(detected_at);
CREATE INDEX IF NOT EXISTS idx_company_signals_score ON company_signals(score);

-- ============================================================
-- 3. Şirket İstihbarat Skorları (Güncel Durum - Materialized View Gibi)
-- ============================================================
CREATE TABLE IF NOT EXISTS company_intelligence_scores (
    company_id                  UUID PRIMARY KEY REFERENCES companies(company_id),
    growth_score                NUMERIC(5,2) DEFAULT 0,           -- Büyüme skoru (0-100)
    expansion_score             NUMERIC(5,2) DEFAULT 0,           -- Coğrafi genişleme skoru
    tech_transformation_score   NUMERIC(5,2) DEFAULT 0,           -- Teknoloji dönüşümü skoru
    investment_signal_score     NUMERIC(5,2) DEFAULT 0,           -- Yatırım sinyali skoru
    org_change_score            NUMERIC(5,2) DEFAULT 0,           -- Organizasyon değişim skoru
    risk_score                  NUMERIC(5,2) DEFAULT 0,           -- Risk skoru (ters)
    hiring_trend                TEXT DEFAULT 'stable',            -- accelerating, stable, decelerating, unknown
    new_locations               JSONB DEFAULT '[]',               -- Yeni açılan şehirler/ülkeler
    new_departments             JSONB DEFAULT '[]',               -- Yeni oluşan departmanlar
    critical_hires              JSONB DEFAULT '[]',               -- Kritik işe alımlar (CTO, VP, Director)
    detected_signals            JSONB DEFAULT '[]',               -- Aktif sinyaller özeti
    signal_count_30d            INTEGER DEFAULT 0,                -- Son 30 gündeki sinyal sayısı
    signal_count_90d            INTEGER DEFAULT 0,                -- Son 90 gündeki sinyal sayısı
    overall_confidence          NUMERIC(5,2) DEFAULT 0,           -- Genel güven skoru
    last_calculated_at          TIMESTAMPTZ DEFAULT NOW(),        -- Son hesaplama tarihi
    updated_at                  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_intel_scores_growth ON company_intelligence_scores(growth_score);
CREATE INDEX IF NOT EXISTS idx_intel_scores_investment ON company_intelligence_scores(investment_signal_score);
CREATE INDEX IF NOT EXISTS idx_intel_scores_risk ON company_intelligence_scores(risk_score);

-- ============================================================
-- 4. Şirket Teknoloji Profili
-- ============================================================
CREATE TABLE IF NOT EXISTS company_tech_profile (
    company_id          UUID PRIMARY KEY REFERENCES companies(company_id),
    technologies        JSONB DEFAULT '{}',                       -- {"Python": 15, "AWS": 8, "Kubernetes": 3, "React": 12}
    tech_categories     JSONB DEFAULT '{}',                       -- {"languages": ["Python", "Java"], "cloud": ["AWS", "Azure"], "frameworks": ["React", "Django"]}
    modernization_signals JSONB DEFAULT '[]',                     -- [{"from": ".NET Framework", "to": ".NET 8", "detected_at": "2026-01-15", "confidence": 85}]
    tech_stack_maturity NUMERIC(5,2) DEFAULT 0,                   -- Teknoloji olgunluğu skoru (0-100)
    innovation_index    NUMERIC(5,2) DEFAULT 0,                   -- Yenilikçilik endeksi
    last_updated        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tech_profile_tech ON company_tech_profile USING GIN (technologies);

-- ============================================================
-- 5. Şirket Alias Tablosu (Eşleştirme için)
-- ============================================================
CREATE TABLE IF NOT EXISTS company_aliases (
    alias_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    alias_name          TEXT NOT NULL,                            -- "Turkcell", "Turkcell A.Ş.", "TURKCELL"
    alias_type          TEXT DEFAULT 'fuzzy',                     -- exact, fuzzy, domain, mersis, manual
    confidence          NUMERIC(5,2) DEFAULT 100,                 -- Eşleşme güveni
    source              TEXT DEFAULT 'system',                    -- system, manual, mersis, gib
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    verified_at         TIMESTAMPTZ,
    verified_by         TEXT,
    UNIQUE(company_id, alias_name)
);

CREATE INDEX IF NOT EXISTS idx_company_aliases_name ON company_aliases(alias_name);
CREATE INDEX IF NOT EXISTS idx_company_aliases_company ON company_aliases(company_id);

-- ============================================================
-- 6. Trigger: company_intelligence_scores updated_at güncelleme
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_company_intel_scores_updated_at ON company_intelligence_scores;
CREATE TRIGGER update_company_intel_scores_updated_at
    BEFORE UPDATE ON company_intelligence_scores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF NOT EXISTS update_company_tech_profile_updated_at ON company_tech_profile;
CREATE TRIGGER update_company_tech_profile_updated_at
    BEFORE UPDATE ON company_tech_profile
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 7. View: Şirket İş İlanı Özeti (Hızlı sorgular için)
-- ============================================================
CREATE OR REPLACE VIEW v_company_job_summary AS
SELECT
    c.company_id,
    c.legal_name,
    c.website_domain,
    COUNT(jp.job_posting_id) AS total_postings,
    COUNT(jp.job_posting_id) FILTER (WHERE jp.posted_at >= NOW() - INTERVAL '30 days') AS postings_30d,
    COUNT(jp.job_posting_id) FILTER (WHERE jp.posted_at >= NOW() - INTERVAL '90 days') AS postings_90d,
    COUNT(DISTINCT jp.location_city) AS unique_cities,
    COUNT(DISTINCT jp.department) AS unique_departments,
    COUNT(DISTINCT jp.technologies) AS unique_tech_count,
    MAX(jp.posted_at) AS latest_posting_date,
    BOOL_OR(jp.seniority_level IN ('director', 'c-level', 'vp', 'head')) AS has_executive_hiring
FROM companies c
LEFT JOIN job_postings jp ON jp.company_id = c.company_id
GROUP BY c.company_id, c.legal_name, c.website_domain;

-- ============================================================
-- 8. View: Aktif Sinyaller Özeti
-- ============================================================
CREATE OR REPLACE VIEW v_company_active_signals AS
SELECT
    cs.company_id,
    c.legal_name,
    cs.signal_type,
    cs.signal_subtype,
    cs.score,
    cs.confidence,
    cs.detected_at,
    cs.valid_until,
    cs.evidence
FROM company_signals cs
JOIN companies c ON c.company_id = cs.company_id
WHERE cs.valid_until IS NULL OR cs.valid_until > NOW()
ORDER BY cs.company_id, cs.score DESC;
