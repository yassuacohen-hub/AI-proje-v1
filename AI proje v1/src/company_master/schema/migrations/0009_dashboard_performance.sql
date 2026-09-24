-- Migration 0009: Dashboard slow query indexes
-- Target: app.py KPI, web_app.py /api/metrics, /api/companies, /api/companies/export

-- Composite index for KPI + filtered lists (is_ankara + is_osb_member + score)
CREATE INDEX IF NOT EXISTS idx_companies_ankara_osb_score
    ON companies(is_ankara, is_osb_member, data_quality_score DESC);

-- Search-supporting indexes for company lookup fields
CREATE INDEX IF NOT EXISTS idx_companies_vergi_no
    ON companies(vergi_no);

CREATE INDEX IF NOT EXISTS idx_companies_primary_phone
    ON companies(primary_phone);

CREATE INDEX IF NOT EXISTS idx_companies_primary_email
    ON companies(primary_email);

CREATE INDEX IF NOT EXISTS idx_companies_web_sitesi
    ON companies(web_sitesi);

-- Expression index for ILIKE/trigram search on legal_name (lowercased)
CREATE INDEX IF NOT EXISTS idx_companies_legal_name_lower
    ON companies(LOWER(legal_name));

-- Expression index for ILIKE/trigram search on trade_name (lowercased)
CREATE INDEX IF NOT EXISTS idx_companies_trade_name_lower
    ON companies(LOWER(trade_name));

-- Export sorting index (created_at DESC)
CREATE INDEX IF NOT EXISTS idx_companies_created_at
    ON companies(created_at DESC);

