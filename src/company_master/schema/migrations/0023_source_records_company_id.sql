-- Migration: source_records.company_id kolonu ekle
-- VERI-KAYNAK-BAG-01: Firma↔kaynak bağı için

-- D-251/5: idempotent olmali. Bu goc elle uygulanmis, deftere yazilmamisti;
-- IF NOT EXISTS olmadigi icin defter onarimi sirasinda patliyordu.
ALTER TABLE source_records ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(company_id);

-- İndeks: eşleme sorgularını hızlandırır
CREATE INDEX IF NOT EXISTS idx_source_records_company_id ON source_records(company_id);