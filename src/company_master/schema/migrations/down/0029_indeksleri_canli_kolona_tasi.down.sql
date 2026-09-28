-- 0029 geri alma: indeksleri terk edilmis kolona geri kur.
-- 0027/0011/0009/0008'deki tanimlarin birebir aynisi.

DROP INDEX IF EXISTS idx_companies_identity_completeness;
CREATE INDEX IF NOT EXISTS idx_companies_quality_score
    ON companies(data_quality_score);

DROP INDEX IF EXISTS idx_companies_ankara_osb_tamlik;
CREATE INDEX IF NOT EXISTS idx_companies_ankara_osb_score
    ON companies(is_ankara, is_osb_member, data_quality_score DESC);

DROP INDEX IF EXISTS idx_companies_source_record_tamlik;
CREATE INDEX IF NOT EXISTS idx_companies_source_record_score
    ON companies(is_ankara, is_osb_member, source_record_id, data_quality_score DESC);

DROP INDEX IF EXISTS idx_companies_dashboard_covering;
CREATE INDEX IF NOT EXISTS idx_companies_dashboard_covering
    ON companies(created_at DESC)
    INCLUDE (data_quality_score, tax_number, website_domain, osb_parcel,
             address, primary_phone, primary_email, nace_code);

DROP INDEX IF EXISTS idx_companies_kpi_covering;
CREATE INDEX IF NOT EXISTS idx_companies_kpi_covering
    ON companies(is_ankara, is_osb_member)
    INCLUDE (data_quality_score, tax_number, website_domain, osb_parcel,
             address, primary_phone, primary_email, nace_code);
