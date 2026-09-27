-- Migration: source_records.company_id kolonu ekle
-- VERI-KAYNAK-BAG-01: Firma↔kaynak bağı için

ALTER TABLE source_records ADD COLUMN company_id UUID REFERENCES companies(company_id);

-- İndeks: eşleme sorgularını hızlandırır
CREATE INDEX idx_source_records_company_id ON source_records(company_id);