-- Migration 0010: Additional performance indexes for dashboard optimization
-- Target: ILIKE search, source filtering, KPI covering

-- Expression indexes for ILIKE search (lowercased)
CREATE INDEX IF NOT EXISTS idx_companies_tax_number_lower
    ON companies(LOWER(tax_number));
CREATE INDEX IF NOT EXISTS idx_companies_vergi_no_lower
    ON companies(LOWER(vergi_no));

-- Source name index (JOIN optimization)
CREATE INDEX IF NOT EXISTS idx_sources_source_name
    ON sources(source_name);

-- Covering index for KPI to avoid heap fetches
CREATE INDEX IF NOT EXISTS idx_companies_kpi_covering
    ON companies(is_ankara, is_osb_member)
    INCLUDE (data_quality_score, tax_number, vergi_no, website_domain, osb_parsel, adres, primary_phone, primary_email, nace_code);
