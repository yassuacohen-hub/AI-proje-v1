-- Migration 0005: source_records → companies izleme sütunu
-- Normalize idempotency: işlenen source_record'ları takip etmek için.
-- Var olan kayıtlarda sütun null kalır (tek seferlik backfill normalize ile işlenir).

ALTER TABLE companies ADD COLUMN IF NOT EXISTS source_record_id UUID REFERENCES source_records(source_record_id);
CREATE INDEX IF NOT EXISTS idx_companies_source_record ON companies(source_record_id);