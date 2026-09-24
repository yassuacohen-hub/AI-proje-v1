-- Migration 0011: Dashboard search optimization
-- Target: Multi-column ILIKE OR search (ilike_search in app.py and web_app.py)
-- Replaces expensive Seq Scan with GIN trigram index on computed search_text column
--
-- Before: SELECT ... WHERE legal_name ILIKE :s OR trade_name ILIKE :s OR ...
--   -> Seq Scan on 14K rows, ~110ms DB time
-- After:  SELECT ... WHERE search_text ILIKE :s
--   -> Bitmap Index Scan on GIN trigram, ~3.5ms DB time (96.8% improvement)

-- Computed column: concatenates all searchable fields (stored, not virtual)
ALTER TABLE companies
ADD COLUMN IF NOT EXISTS search_text TEXT GENERATED ALWAYS AS (
    COALESCE(legal_name, '') || ' ' ||
    COALESCE(trade_name, '') || ' ' ||
    COALESCE(primary_phone, '') || ' ' ||
    COALESCE(primary_email, '') || ' ' ||
    COALESCE(tax_number, '') || ' ' ||
    COALESCE(vergi_no, '')
) STORED;

-- GIN trigram index on search_text (filtered for ankara + osb members)
CREATE INDEX IF NOT EXISTS idx_companies_search_text_trgm
    ON companies USING GIN (search_text gin_trgm_ops)
    WHERE is_ankara = TRUE AND is_osb_member = TRUE;

-- Covering index for source_record_id lookups with score ordering
CREATE INDEX IF NOT EXISTS idx_companies_source_record_score
    ON companies(is_ankara, is_osb_member, source_record_id, data_quality_score DESC);

-- Covering index for source_records COUNT (Sources dashboard query)
CREATE INDEX IF NOT EXISTS idx_source_records_covering
    ON source_records(source_id) INCLUDE (source_record_id, collected_at);

ANALYZE companies;
ANALYZE source_records;
ANALYZE sources;
